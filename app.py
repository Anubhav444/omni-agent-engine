import os
import re
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from google import genai
from google.genai import types

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

SYSTEM_PROMPT = """You are OmniAgent, the smart AI consultant representing Sinha AI Tech Solutions.
Services Offered:
- Custom Business Website Development & AI Chatbot Integration
- Automated Recruitment & Screening Systems
- Business Workflow Automation

Instructions:
1. Always reply in the same language the user uses (Hindi, English, or Hinglish).
2. Answer naturally and conversationally in 1-2 sentences.
3. Help users with their requests (like website design, AI integration) and ask for their Email or Phone number to arrange a discovery call."""

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
    
    if re.search(email_pattern, user_text) or re.search(phone_pattern, user_text):
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": f"🚀 *New Lead Captured! (Sinha AI Tech Solutions)*\n\n👤 *Message:* {user_text}",
                "parse_mode": "Markdown"
            }
            requests.post(url, json=payload, timeout=5)
        except Exception:
            pass

@app.get("/")
def home():
    return {"status": "OmniAgent Engine is Active"}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    if not API_KEY:
        return {"reply": "Server Error: API Key missing."}
    
    check_and_send_lead_alert(req.message, req.history)
    
    try:
        client = genai.Client(api_key=API_KEY)
        
        contents = []
        for item in req.history[-6:]:
            role = "user" if item.role == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=item.content)]))
        
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=req.message)]))
        
        # Updated to gemini-3.6-flash as requested by API
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7
            )
        )
        
        if response and response.text:
            return {"reply": response.text.strip()}
            
    except Exception as e:
        return {"reply": f"Live Engine Error: {str(e)}"}
        
    return {"reply": "Hum aapke business ke liye high-converting website aur AI solutions develop karte hain. Aap kis type ki website chahte hain?"}
