from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import json
import os
import uuid
from typing import List

app = FastAPI(title="Digital Twin Career Engine API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
CAREER_DATA_PATH = os.path.join(BASE_DIR, "career_advisor", "career_prediction.json")
CHAT_HISTORY_PATH = os.path.join(BASE_DIR, "backend", "chat_history.json")

# Pydantic Models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    api_key: str
    session_id: str = "default"

class SessionUpdate(BaseModel):
    title: str

SYSTEM_PROMPT = """Ты — Digital Twin Career Engine Актана Кадыркулова. Ты его личный AI-карьерный коуч и цифровой двойник. 
Ты хорошо знаешь его: студент IT в Alatoo University, работает барменом, профи в Figma, UI/UX, Illustrator, учит Godot и HTML/CSS.
Отвечай мотивирующе, по делу. Если просят roast — делай это смешно и жестко."""

# API ENDPOINTS

@app.get("/api/prediction")
async def get_prediction():
    if os.path.exists(CAREER_DATA_PATH):
        try:
            with open(CAREER_DATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"top_3_jobs": [], "priority_skills_to_learn": []}

@app.get("/api/skills")
async def get_skills():
    return {
        "categories": ['Figma', 'UI/UX Design', 'Godot', 'HTML/CSS', 'Illustrator', 'Prototyping', 'Teamwork', 'Communication', 'Responsibility', 'Problem Solving', 'Creativity'],
        "hard_skills": [90, 75, 60, 70, 85, 80, 0, 0, 0, 0, 0],
        "soft_skills": [0, 0, 0, 0, 0, 0, 85, 80, 90, 70, 75]
    }

@app.get("/api/history")
async def get_history():
    if os.path.exists(CHAT_HISTORY_PATH):
        try:
            with open(CHAT_HISTORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "sessions" in data:
                    return data
        except: pass
    return {"sessions": []}

@app.post("/api/sessions")
async def create_session():
    data = {"sessions": []}
    if os.path.exists(CHAT_HISTORY_PATH):
        try:
            with open(CHAT_HISTORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except: pass
    
    new_session = {"id": str(uuid.uuid4()), "title": "Новый чат", "messages": []}
    if not isinstance(data, dict): data = {"sessions": []}
    data["sessions"].insert(0, new_session)
    
    with open(CHAT_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return new_session

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    if os.path.exists(CHAT_HISTORY_PATH):
        try:
            with open(CHAT_HISTORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data["sessions"] = [s for s in data["sessions"] if s["id"] != session_id]
                with open(CHAT_HISTORY_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except: pass
    return {"status": "deleted"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        client = Groq(api_key=request.api_key)
        
        # Extremely robust message building
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in request.messages:
            role = getattr(m, "role", "user")
            content = getattr(m, "content", "")
            api_messages.append({"role": role, "content": content})
            
        completion = client.chat.completions.create(
            messages=api_messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1024,
        )
        
        # Robust response parsing
        choice = completion.choices[0]
        ai_response = getattr(choice.message, "content", "")
        if not ai_response: # Fallback for dict-like
            ai_response = choice["message"]["content"]

        # Save to history
        if os.path.exists(CHAT_HISTORY_PATH):
            with open(CHAT_HISTORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, dict) and "sessions" in data:
                for s in data["sessions"]:
                    if s["id"] == request.session_id:
                        user_txt = request.messages[-1].content
                        if len(s["messages"]) == 0:
                            s["title"] = (user_txt[:25] + "...") if len(user_txt) > 25 else user_txt
                        s["messages"].append({"role": "user", "content": user_txt})
                        s["messages"].append({"role": "assistant", "content": ai_response})
                        break
                
                with open(CHAT_HISTORY_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

        return {"response": ai_response}
        
    except Exception as e:
        # Final fallback error message
        import traceback
        error_details = traceback.format_exc()
        print(error_details)
        raise HTTPException(status_code=500, detail=f"Groq Error: {str(e)}")

if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
