import os
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

SYSTEM_PROMPT = """You are OmniAgent, the official AI business representative for Sinha AI Tech Solutions.
Our Core Services: Custom AI Chatbots & Agents, Automated Recruitment Systems, and Business Process Automation.
Guidelines: Answer visitor queries professionally and concisely (under 3 sentences) and prompt them for their Name and Email/Phone to schedule a free consultation."""

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[Message]
    message: str

@app.get("/")
def home():
    return {"status": "OmniAgent Engine is Active & Running"}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    if not API_KEY:
        return {"reply": "API Key is not configured on the server."}
    
    # Official updated endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{SYSTEM_PROMPT}\n\nVisitor: {req.message}"}
                ]
            }
        ]
    }
    
    try:
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        data = res.json()
        
        if "candidates" in data and len(data["candidates"]) > 0:
            bot_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"reply": bot_text.strip()}
        elif "error" in data:
            return {"reply": f"API Error: {data['error'].get('message', 'Model error')}"}
        else:
            return {"reply": "Hello! How can I assist you with Sinha AI Tech Solutions today?"}
            
    except Exception as e:
        return {"reply": f"Connection error: {str(e)}"}
