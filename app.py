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

SYSTEM_PROMPT = """You are OmniAgent, the AI business representative for Sinha AI Tech Solutions.
Core Services: Custom AI Chatbots, Automated Recruitment Systems, and Business Process Automation.
Goal: Answer visitor queries professionally and concisely (under 3 sentences) and prompt them for their Name and Email to schedule a consultation."""

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
    
    # List of stable fallback models in priority order
    candidate_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]
    
    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": f"{SYSTEM_PROMPT}\n\nVisitor: {req.message}"}]
                }
            ]
        }
        
        try:
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
            data = res.json()
            
            if "candidates" in data and len(data["candidates"]) > 0:
                bot_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return {"reply": bot_text.strip()}
            elif "error" in data:
                # If model is deprecated/unavailable, try next model in candidate_models
                continue
        except Exception:
            continue

    return {"reply": "Hello! Welcome to Sinha AI Tech Solutions. How can we help automate your business today? Please share your name and email to connect with us."}
