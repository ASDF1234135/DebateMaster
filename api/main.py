from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uuid
import json
import asyncio
from Agent.core import run_debate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 之後正式上線再改成你的前端網址 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}


# 1. GET /
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Debate Master API is running.",
    }


# 2. POST /api/v1/debate/start
@app.post("/api/v1/debate/start")
async def start_debate(
    prompt: str = Form(...),
    opponent_persona: str = Form(...),
    max_rounds: int = Form(...),
    trial: int = Form(...),
    file: Optional[UploadFile] = File(None)
):
    context = None

    if file:
        file_bytes = await file.read()
        context = file_bytes.decode("utf-8", errors="ignore")

    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "session_id": session_id,
        "prompt": prompt,
        "opponent_persona": opponent_persona,
        "max_rounds": max_rounds,
        "trial": trial,
        "context": context
    }

    return {
        "status": "success",
        "session_id": session_id,
        "message": "Debate session created successfully."
    }


def format_sse(data: dict):
    return f"event: message\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


# 3. GET /api/v1/debate/stream/{session_id}
@app.get("/api/v1/debate/stream/{session_id}")
async def stream_debate(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session_config = sessions[session_id]

    async def event_generator():
        try:
            async for ai_event in run_debate(session_config):
                yield format_sse(ai_event)
                
            
        except Exception as e:
            error_data = {
                "type": "error",
                "message": f"AI core error: {str(e)}"
            }
            yield format_sse(error_data)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

#4. GET /api/v1/debates
@app.get("/api/v1/debates")
async def get_debates():

    try:
        debates = get_all_debates()

        return {
            "status": "success",
            "data": debates
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch debates: {str(e)}"
        )

# 5. GET /api/v1/debates/{session_id}/messages
@app.get("/api/v1/debates/{session_id}/messages")
async def get_debate_messages_api(session_id: str):

    try:
        messages = get_debate_messages(session_id)

        return {
            "status": "success",
            "data": messages
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch messages: {str(e)}"
        )