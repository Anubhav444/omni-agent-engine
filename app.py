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

SYSTEM_PROMPT = """You are OmniAgent, the professional AI business representative for Sinha AI Tech Solutions.
Services: Custom AI Chatbots, Automated Recruitment Systems, and Business Process Automation.
Instructions: Speak naturally, keep answers under 2 sentences, and help users with inquiries."""

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
                "text": f"🚀 *New Lead Captured!*\n\nMessage: {user_text}",
                "parse_mode": "Markdown"
            }
            requests.post(url, json=payload, timeout=5)
        except Exception:
            pass

@app.get("/")
def home():
    return {"status": "OmniAgent Engine is Live"}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    if not API_KEY:
        return {"reply": "Error: GEMINI_API_KEY is missing on Render environment variables."}
    
    check_and_send_lead_alert(req.message, req.history)
    
    try:
        client = genai.Client(api_key=API_KEY)
        
        contents = []
        for item in req.history[-6:]:
            role = "user" if item.role == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=item.content)]))
        
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=req.message)]))
        
        # Using stable gemini-2.5-flash model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7
            )
        )
        
        if response and response.text:
            return {"reply": response.text.strip()}
            
    except Exception as e:
        # Return exact error message to chat window for debugging
        return {"reply": f"API Error: {str(e)}"}
        
    return {"reply": "Hello! Welcome to Sinha AI Tech Solutions. How can I help you?"}
