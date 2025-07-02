import streamlit as st
import uuid
from mental_health_bot import graph

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state.history = []

st.set_page_config(page_title="Therapy-Lite Chatbot", page_icon="🫀")
st.title("🫀 Therapy-Lite Chatbot")
st.markdown("Chat with a warm, empathetic assistant who cares about your well-being.")

# Display previous messages
for i, pair in enumerate(st.session_state.history):
    st.markdown(f"**You:** {pair['user']}")
    st.markdown(f"**🫀 Bot:** {pair['bot']}")

# User input
user_input = st.chat_input("How are you feeling today?")

if user_input:
    with st.spinner("Thinking..."):
        result = graph.invoke({
            "user_input": user_input,
            "session_id": st.session_state.session_id,
            "history": [f"You: {m['user']}\nBot: {m['bot']}" for m in st.session_state.history]
        })

        reply = result.get("reply", "I'm here to listen.")

        st.session_state.history.append({
            "user": user_input,
            "bot": reply
        })

        # Rerun to immediately show the new message
        st.rerun()
