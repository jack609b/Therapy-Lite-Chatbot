# 🧠 Therapy-Lite Chatbot

A compassionate, therapy-style mental health chatbot built using **LangGraph**, **OpenAI GPT-4o**, **MongoDB**, and **Streamlit**.
It supports empathetic conversation, detects emotional state, evaluates risk, offers coping strategies (when needed), and stores session history.

---

## 💡 Features

* 🧑‍⚕️ Therapist-style empathetic replies
* 🔍 Emotion detection from context-aware history
* ⚠️ Suicide/self-harm risk assessment
* 🧘‍♀️ Conditional coping strategies
* 💾 MongoDB-based session tracking with UUIDs
* 🔁 Memory: Maintains recent conversation context (last 5 messages)
* 🖥️ Streamlit GUI for easy interaction

---

## 📦 Installation

1. **Clone the repo**

```bash
git clone https://github.com/your-username/therapy-lite-chatbot.git
cd therapy-lite-chatbot
```

2. **Set up virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Add `.env` file**

Create a `.env` file with the following:

```
OPENAI_API_KEY=your_openai_key
MONGO_URI=your_mongodb_connection_string
```

---

## 🚀 Run the Chatbot

```bash
streamlit run app.py
```

---

## 🗂️ Project Structure

```
.
├── app.py                 # Streamlit interface
├── mental_health_bot.py  # LangGraph logic and workflow
├── requirements.txt
└── .env                  # (Your secrets)
```

---

## 🧪 Example Usage

```text
You: I feel so overwhelmed lately.
🤖: That sounds really tough. Would you like to share what’s been weighing you down?

Coping Tip: Take a short walk outdoors and breathe deeply to reset your nervous system.
```

---

## 🛡 Disclaimer

This chatbot is **not a substitute for professional therapy** or crisis support.
If you or someone you know is in immediate danger or requires urgent help, please reach out to a qualified mental health professional or helpline.

---

## 📚 Tech Stack

* [LangGraph](https://github.com/langchain-ai/langgraph)
* [LangChain](https://github.com/langchain-ai/langchain)
* [OpenAI GPT-4o](https://platform.openai.com/docs)
* [MongoDB](https://www.mongodb.com/)
* [Streamlit](https://streamlit.io/)

---

## 🧠 Inspiration

Built for those exploring compassionate AI systems in the mental health and wellbeing space.
Inspired by AI agents that can remember, reason, and reflect.

