from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uuid
import json

from Agent.core import run_debate

# 匯入你的 DB 寫入工具
from DB.save_debate_to_db import (
    DebateDBWriter,
    normalize_session_config,
    normalize_conversation_event,
    normalize_summary_event,
)

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
    file_name = None

    if file:
        file_bytes = await file.read()
        context = file_bytes.decode("utf-8", errors="ignore")
        file_name = file.filename

    session_id = str(uuid.uuid4())

    # 先維持你原本的 sessions 記憶體結構
    sessions[session_id] = {
        "session_id": session_id,
        "prompt": prompt,
        "opponent_persona": opponent_persona,
        "max_rounds": max_rounds,
        "trial": trial,
        "context": context,
        "file_name": file_name,
        "my_persona": None,   # 你目前前端沒傳就先放 None
    }

    # 新增：寫入 debate_sessions
    db = DebateDBWriter()
    try:
        session_config = normalize_session_config(sessions[session_id])
        db.insert_session(session_config)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save debate session: {str(e)}")
    finally:
        db.close()

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
        db = DebateDBWriter()
        sequence_no = 1

        try:
            async for ai_event in run_debate(session_config):
                event_type = ai_event.get("type")

                # 1) init event：不寫 DB，直接傳前端
                if event_type == "init":
                    yield format_sse(ai_event)

                # 2) conversation：寫入 debate_messages，再傳前端
                elif event_type == "conversation":
                    normalized_event = normalize_conversation_event(ai_event)
                    db.insert_message(session_id, normalized_event, sequence_no)
                    db.commit()

                    sequence_no += 1
                    yield format_sse(ai_event)

                # 3) summary：寫入 debate_summaries，再傳前端
                elif event_type == "summary":
                    normalized_event = normalize_summary_event(ai_event)
                    db.insert_summary(session_id, normalized_event)
                    db.commit()

                    yield format_sse(ai_event)

                # 4) 其他未知 event：先直接傳前端
                else:
                    yield format_sse(ai_event)

        except Exception as e:
            db.rollback()
            error_data = {
                "type": "error",
                "message": f"AI core error: {str(e)}"
            }
            yield format_sse(error_data)

        finally:
            db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )