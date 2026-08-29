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

@app.get("/")
def home():
    return {"status": "OmniAgent Engine is Active & Running"}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    if not API_KEY:
        return {"reply": "API Key is missing on the server."}
    
    # Construct conversational context
    formatted_contents = [
        {"parts": [{"text": f"System Context: {SYSTEM_PROMPT}"}]}
    ]
    
    # Add previous chat history
    for item in req.history[-6:]:  # Keep last 6 exchanges for context
        role = "user" if item.role == "user" else "model"
        formatted_contents.append({"parts": [{"text": f"{role}: {item.content}"}]})
    
    # Add latest user message
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
