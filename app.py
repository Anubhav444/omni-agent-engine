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

TELEGRAM_BOT_TOKEN = "8628786968:AAFgEBxwqwdh6SD-qtdzMtTXlMJr65ZA7X0"
TELEGRAM_CHAT_ID = "5989832945"

# Optimized System Prompt for dynamic, engaging conversations
SYSTEM_PROMPT = """You are OmniAgent, the engaging and intelligent AI business consultant for Sinha AI Tech Solutions.
Services Offered: Custom AI Chatbots, Automated Recruitment Systems, and Business Process Automation.

Instructions:
1. Converse naturally like a consultant, avoiding repetitive or robotic phrases.
2. Maintain strong conversation context from the chat history.
3. If the user gives short responses (e.g., 'ok', 'thank you', 'yes', 'hello'), respond naturally to keep the dialogue moving.
4. Keep responses concise (1-2 sentences). Guide high-intent prospects to share Email or Phone number."""

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[Message]
    message: str

def check_and_send_lead_alert(user_text: str, chat_history: List[Message]):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'(\+?[0-9]{1,3}[-.\s]?)?(\(?\d{3,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{4,6}'
    
    # Send lead if Email or Phone number detected
    if re.search(email_pattern, user_text) or re.search(phone_pattern, user_text):
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            # Include recent chat history for context in Telegram alert
            context_summary = "\n".join([f"• {m.role}: {m.content}" for m in chat_history[-3:]])
            
            alert_msg = (
                f"🚀 *New Lead Captured! (Sinha AI Tech Solutions)*\n\n"
                f"👤 *Latest Message:* {user_text}\n\n"
                f"💬 *Recent Context:*\n{context_summary}"
            )
            
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": alert_msg,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=payload, timeout=5)
        except Exception:
            pass

@app.get("/")
def home():
    return {"status": "OmniAgent Engine is Online"}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    if not API_KEY:
        return {"reply": "Server Error: API Key is missing."}
    
    check_and_send_lead_alert(req.message, req.history)
    
    # Official Gemini v1beta REST API structure with System Instructions
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    formatted_contents = []
    # Add System Prompt as 'systemInstruction'
    formatted_contents.append({
        "role": "user",
        "parts": [{"text": f"System Context: {SYSTEM_PROMPT}"}]
    })
    
    # Add conversation history
    for item in req.history[-6:]:
        role = "user" if item.role == "user" else "model"
        formatted_contents.append({
            "role": role,
            "parts": [{"text": item.content}]
        })
        
    # Add current user message
    formatted_contents.append({
        "role": "user",
        "parts": [{"text": req.message}]
    })
    
    payload = {
        "contents": formatted_contents
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=12)
        data = response.json()
        
        # Extract reply from stable v1beta response structure
        if response.status_code == 200 and "candidates" in data and len(data["candidates"]) > 0:
            bot_reply = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"reply": bot_reply.strip()}
            
    except Exception as e:
        print("API Error:", e)
        
    # Smart default fallback that continues conversation naturally
    return {"reply": "Got it. What aspect of our AI solutions are you interested in exploring next?"}
