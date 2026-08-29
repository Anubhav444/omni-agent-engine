import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from google import genai

app = FastAPI(title="OmniAgent Engine", version="1.0")

# Enable Cross-Origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Gemini API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Client Business Training & Instructions
SYSTEM_INSTRUCTION = """
You are OmniAgent, the 24/7 AI Business Representative for [Client Company Name].

Company Info & Services:
- Business: [Insert Client Business description here]
- Services: [List of Services & Pricing]
- Target Audience: Global startups, businesses, and individuals.

Your Primary Goals:
1. Answer visitor questions clearly, politely, and within 2 to 3 sentences.
2. Skillfully ask for their Name, Business Email, and Project Requirements.
3. Once the user provides contact details, confirm receipt and thank them.

Tone: Professional, modern, concise, and helpful.
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
        # Prepare context + conversation history
        prompt_content = f"System Rules: {SYSTEM_INSTRUCTION}\n\nChat History:\n"
        for msg in req.history:
            prompt_content += f"{msg.role}: {msg.content}\n"
        prompt_content += f"user: {req.message}\nassistant:"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_content
        )
        return {"reply": response.text.strip()}
    except Exception as e:
        return {"reply": "I apologize, but I am momentarily experiencing network delay. Please leave your email and we will contact you shortly."}
