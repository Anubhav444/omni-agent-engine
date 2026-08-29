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
Services offered: Custom AI Agent Development, Recruitment Automation, and Enterprise Process Optimization.
Goal: Answer visitor queries professionally and concisely in 2-3 sentences, then ask for their Name and Email/Phone to book a consultation."""

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[Message]
    message: str

def find_active_model():
    """Fetch the exact valid model name from Google AI API"""
    try:
        res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}", timeout=5)
        data = res.json()
        if "models" in data:
            for m in data["models"]:
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods:
                    return m["name"]  # e.g., 'models/gemini-3.6-flash'
    except Exception:
        pass
    return "models/gemini-3.6-flash"

@app.get("/")
def home():
    return {"status": "OmniAgent Engine is Active & Running"}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    if not API_KEY:
        return {"reply": "Server error: API Key is not configured."}
    
    # Get active model dynamically
    model_path = find_active_model()
    
    # Clean up model path format
    if not model_path.startswith("models/"):
        model_path = f"models/{model_path}"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_path}:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{SYSTEM_PROMPT}\n\nUser Question: {req.message}"}
                ]
            }
        ]
    }
    
    try:
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        data = res.json()
        
        if res.status_code == 200 and "candidates" in data and len(data["candidates"]) > 0:
            reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"reply": reply_text.strip()}
        elif "error" in data:
            return {"reply": f"API Notice: {data['error'].get('message', 'Processing error')}"}
        else:
            return {"reply": "Hello! How can I assist you with Sinha AI Tech Solutions today?"}
            
    except Exception as e:
        return {"reply": f"Connection Error: {str(e)}"}
