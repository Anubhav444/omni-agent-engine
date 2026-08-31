import os
import re
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="OmniAgent Engine", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("GEMINI_API_KEY")

# Embedded Telegram Credentials
TELEGRAM_BOT_TOKEN = "8628786968:AAFgEBxwqwdh6SD-qtdzMtTXlMJr65ZA7X0"
TELEGRAM_CHAT_ID = "5989832945"

SYSTEM_PROMPT = """You are OmniAgent, the intelligent AI business representative for Sinha AI Tech Solutions.
Services: Custom AI Chatbots & Agents, Automated Recruitment Systems, and Business Process Automation.
Behavior Instructions:
1. Have an engaging, natural, human-like conversation. Remember what the user said previously.
2. If the user shares details, acknowledges something, or says short words like 'ok', 'yes', 'cool', respond naturally to continue the discussion without repeating your whole sales pitch.
3. Keep responses concise (1-3 sentences)."""

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[Message]
    message: str

def check_and_send_lead_alert(user_text: str, chat_history: List[Message]):
    """Detects emails or phone numbers and sends instant Telegram alert"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    # Regex patterns for email and phone numbers (7 to 15 digits)
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'(\+?[0-9]{1,3}[-.\s]?)?(\(?\d{3,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{4,6}'

    has_email = re.search(email_pattern, user_text)
    has_phone = re.search(phone_pattern, user_text)

    if has_email or (has_phone and len(re.sub(r'\D', '', user_text)) >= 10):
        context_summary = "\n".join([f"• {m.role}: {m.content}" for m in chat_history[-3:]])
        
        alert_msg = (
            f"🚀 *New Lead Captured! (Sinha AI Tech Solutions)*\n\n"
            f"👤 *Latest Message:* {user_text}\n\n"
            f"💬 *Recent Context:*\n{context_summary}\n\n"
            f"⚡ *Action:* Reach out to client immediately!"
        )
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": alert_msg,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception:
            pass

@app.get("/")
def home():
    return {"status": "OmniAgent Engine is Active & Running"}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    if not API_KEY:
        return {"reply": "API Key is missing on the server."}
    
    # Trigger instant lead detection & notification
    check_and_send_lead_alert(req.message, req.history)
    
    # Construct conversational context
    formatted_contents = [
        {"parts": [{"text": f"System Context: {SYSTEM_PROMPT}"}]}
    ]
    
    for item in req.history[-6:]:
        role = "user" if item.role == "user" else "model"
        formatted_contents.append({"parts": [{"text": f"{role}: {item.content}"}]})
    
    formatted_contents.append({"parts": [{"text": f"user: {req.message}"}]})

    payload = {
        "contents": formatted_contents
    }
    
    models = ["gemini-3.6-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
        try:
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=12)
            data = res.json()
            
            if res.status_code == 200 and "candidates" in data and len(data["candidates"]) > 0:
                bot_reply = data["candidates"][0]["content"]["parts"][0]["text"]
                return {"reply": bot_reply.strip()}
        except Exception:
            continue
            
    return {"reply": "Got it! How else can I assist you?"}
