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
Our Services: Custom AI Chatbots & Agents, Automated Recruitment Systems, and Business Process Automation.
Goal: Answer visitor questions concisely and politely in 2-3 sentences, then ask for their Name and Email to book a consultation."""

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
    
    # Priority list of models to try
    models = ["gemini-3.6-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{SYSTEM_PROMPT}\n\nVisitor Message: {req.message}"}
                ]
            }
        ]
    }
    
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
        try:
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=12)
            data = res.json()
            
            # Check if successful response received
            if res.status_code == 200 and "candidates" in data and len(data["candidates"]) > 0:
                bot_reply = data["candidates"][0]["content"]["parts"][0]["text"]
                return {"reply": bot_reply.strip()}
        except Exception:
            continue
            
    return {"reply": "Hello! We provide AI Agents and Business Automation solutions at Sinha AI Tech Solutions. How can we assist your business today?"}
