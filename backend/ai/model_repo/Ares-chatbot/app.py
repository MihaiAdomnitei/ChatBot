import random

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from patient_engine import PatientChatEngine
from chat_manager import ChatManager
from patient_profiles import PATIENT_PROFILES
from prompt_builder import build_patient_prompt
from patology_enum import PathologyEnum

import uvicorn

# ----------------------------
# App initialization
# ----------------------------

app = FastAPI(title="Patient Simulator API")

engine: PatientChatEngine | None = None
chat_manager = ChatManager()


# ----------------------------
# Models
# ----------------------------

class NewChatRequest(BaseModel):
    pathology: str


class MessageRequest(BaseModel):
    message: str
    max_new_tokens: int = 25  # Reduced for faster CPU inference

# ----------------------------
# Startup event (LOAD MODEL)
# ----------------------------

@app.on_event("startup")
def startup_event():
    global engine
    print("🚀 Loading PatientChatEngine...")
    engine = PatientChatEngine()
    print("✅ Model loaded successfully")

# ----------------------------
# Routes
# ----------------------------

@app.post("/chats")
def create_chat():
    pathology = random.choice(list(PathologyEnum)).name.lower()
    profile = PATIENT_PROFILES.get(pathology)

    if not profile:
        raise HTTPException(status_code=400, detail="Unknown pathology")

    system_prompt = build_patient_prompt(
        pathology_label=profile["label"],
        mf=profile
    )

    chat_id = chat_manager.create_chat(system_prompt)
    return {
        "chat_id": chat_id,
        "pathology": pathology
    }

@app.post("/chats/{chat_id}/message")
def send_message(chat_id: str, req: MessageRequest):
    if engine is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    messages = chat_manager.get_messages(chat_id)
    if messages is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    chat_manager.add_user(chat_id, req.message)

    reply = engine.generate(
        messages=chat_manager.get_messages(chat_id),
        max_new_tokens=req.max_new_tokens
    )

    chat_manager.add_assistant(chat_id, reply)
    return {"reply": reply}

@app.get("/chats/{chat_id}")
def get_chat(chat_id: str):
    messages = chat_manager.get_messages(chat_id)
    if messages is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"messages": messages}

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "model_loaded": engine is not None
    }

# ----------------------------
# Run server directly
# ----------------------------

if __name__ == "__main__":
    uvicorn.run(
        "app:app",  # adjust if your path is different
        host="0.0.0.0",
        port=8000,
        reload=False
    )