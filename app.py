import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import google.generativeai as genai

app = FastAPI(title="OmniAgent Engine", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """You are OmniAgent, the official AI representative for Sinha AI Tech Solutions.
We provide: Custom AI Agents, Automated Recruitment Systems, and Business Process Automation.
Goal: Answer the user's question politely and concisely (under 3 sentences) and ask for their name and email to get started."""

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
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Combine prompt with context
        conversation = f"{SYSTEM_PROMPT}\n\nUser: {req.message}"
        response = model.generate_content(conversation)
        
        return {"reply": response.text.strip()}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {"reply": f"Agent error: {str(e)}"}
