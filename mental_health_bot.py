import os
import re
import json
import pymongo
import uuid
from dotenv import load_dotenv
from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import unicodedata
import sys

# Load environment variables
load_dotenv()

# Initialize OpenAI Chat Model
llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize MongoDB Client
mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = mongo_client["therapy_bot"]
session_collection = db["sessions"]

# Define the state schema
class ChatState(TypedDict):
    user_input: str
    session_id: str
    history: Optional[List[str]]
    emotion: Optional[str]
    risk: Optional[str]
    reply: Optional[str]

# Node 1: Detect Emotion
def detect_emotion(state: ChatState) -> dict:
    context = "\n".join(state.get("history", [])[-5:])
    prompt = ChatPromptTemplate.from_template("""
    Given the user's message and recent chat history, detect their emotion: happy, sad, anxious, angry, neutral.
    Chat History:
    {context}
    Message: {text}
    Return JSON: {{"emotion": "emotion_value"}}
    """)
    res = llm.invoke(prompt.format_messages(text=state["user_input"], context=context)).content
    match = re.search(r"{.*}", res)
    if not match:
        print("⚠️ LLM failed to return valid JSON for emotion. Raw output:", res)
        return {"emotion": "neutral"}
    try:
        emotion = json.loads(match.group())["emotion"]
        return {"emotion": emotion}
    except Exception as e:
        print("⚠️ JSON parsing failed:", e, "Raw response:", res)
        return {"emotion": "neutral"}

# Node 2: Respond as Therapist with Follow-ups and Empathy
def respond_empathically(state: ChatState) -> dict:
    context = "\n".join(state.get("history", [])[-5:])
    prompt = ChatPromptTemplate.from_template("""
    You are a warm and empathetic therapist. Respond to the user’s message based on their current emotion: {emotion}.
    Use a caring tone and try to ask a gentle follow-up question that encourages the user to open up.
    Be supportive and validating, not robotic.
    Message: {text}
    Chat History:
    {context}
    """)
    reply = llm.invoke(prompt.format_messages(
        text=state["user_input"], 
        emotion=state["emotion"],
        context=context
    )).content
    return {"reply": reply}

# Node 3: Check for Risk
def check_for_risk(state: ChatState) -> dict:
    prompt = ChatPromptTemplate.from_template("""
You are a mental health assistant. Based on the message, assess the risk of self-harm or suicidal intent.

Message: {text}

Respond only with valid JSON like this:
{{"risk": "none"}}  # or "low" or "high"

Return only the JSON. Do not include any explanation.
""")

    res = llm.invoke(prompt.format_messages(text=state["user_input"])).content
    
    match = re.search(r"{.*}", res)
    if not match:
        # print("⚠️ LLM failed to return valid JSON for risk. Raw output:", res)
        return {"risk": "none"}
    try:
        risk = json.loads(match.group())["risk"]
        return {"risk": risk}
    except Exception as e:
        print("⚠️ JSON parsing failed:", e, "Raw response:", res)
        return {"risk": "none"}

# Node 4: Offer Coping Tip only if relevant
def offer_coping_tip_if_needed(state: ChatState) -> dict:
    prompt = ChatPromptTemplate.from_template("""
    Based on this user message, if you think they could benefit from a coping strategy, suggest one helpful and practical tip.
    Otherwise return: {{"tip": null}}
    Message: {text}
    Return JSON: {{"tip": "short coping tip"}} or {{"tip": null}}
    """)
    res = llm.invoke(prompt.format_messages(text=state["user_input"])).content
    match = re.search(r"{.*}", res)
    if not match:
        return {}
    try:
        tip_data = json.loads(match.group())
        tip = tip_data.get("tip")
        if tip:
            return {"reply": state["reply"] + f"\n\nCoping Tip: {tip}"}
        return {}
    except Exception as e:
        print("⚠️ JSON parse failed for tip:", e)
        return {}

# Node 5: Alert or Continue
def alert_or_continue(state: ChatState) -> dict:
    if state["risk"] == "high":
        return {
            "reply": state["reply"] + "\n\n🚨 You may be experiencing a crisis. Please consider contacting a mental health professional or helpline like 9152987821 (India)."
        }
    return {}

# Node 6: Store Chat in MongoDB
def clean_text(text):
    return unicodedata.normalize("NFKD", text).encode("utf-8", "ignore").decode("utf-8")

def store_chat(state: ChatState) -> dict:
    cleaned_input = clean_text(state["user_input"])
    cleaned_reply = clean_text(state["reply"])

    session_collection.update_one(
        {"session_id": state["session_id"]},
        {"$push": {"messages": {"user": cleaned_input, "bot": cleaned_reply}}, "$setOnInsert": {"session_id": state["session_id"]}},
        upsert=True
    )
    return {}

def safe_print(text):
    safe_text = unicodedata.normalize("NFKD", text).encode("utf-8", "ignore").decode("utf-8")
    print("🤖:", safe_text)

# Build LangGraph workflow
workflow = StateGraph(ChatState)
workflow.add_node("detect_emotion", detect_emotion)
workflow.add_node("respond", respond_empathically)
workflow.add_node("check_risk", check_for_risk)
workflow.add_node("coping_tip", offer_coping_tip_if_needed)
workflow.add_node("alert_or_continue", alert_or_continue)
workflow.add_node("save", store_chat)

# Define flow
workflow.set_entry_point("detect_emotion")
workflow.add_edge("detect_emotion", "respond")
workflow.add_edge("respond", "check_risk")
workflow.add_edge("check_risk", "coping_tip")
workflow.add_edge("coping_tip", "alert_or_continue")
workflow.add_edge("alert_or_continue", "save")
workflow.add_edge("save", END)

# Compile graph
graph = workflow.compile()

# Main function to run
if __name__ == "__main__":
    session_id = str(uuid.uuid4())
    history = []

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        result = graph.invoke({
            "user_input": user_input,
            "session_id": session_id,
            "history": history
        })

        reply = result.get("reply", "I'm here to listen.")
        safe_print(reply)
        history.append(f"You: {user_input}\nBot: {reply}")
