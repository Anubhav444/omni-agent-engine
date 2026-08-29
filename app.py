import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import google.generativeai as genai

app = FastAPI(title="OmniAgent Engine", version="1.0")

# Cross-Origin permissions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

SYSTEM_INSTRUCTION = """
You are OmniAgent, the 24/7 AI Business Representative for Sinha AI Tech Solutions.
Services offered: AI Agent Development, Recruitment Automation, Global Process Optimization.
Goal: Answer visitor questions professionally in 2-3 sentences and ask for their Name and Email to book a consultation.
"""

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
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        # Build conversational context
        chat_context = ""
        for msg in req.history:
            chat_context += f"{msg.role}: {msg.content}\n"
        chat_context += f"user: {req.message}"
        
        response = model.generate_content(chat_context)
        return {"reply": response.text.strip()}
    except Exception as e:
        return {"reply": "I am experiencing a brief connection delay. Please leave your contact details."}
