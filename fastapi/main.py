from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uuid
import json
import asyncio

app = FastAPI()

# 讓前端可以連線
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 之後正式上線再改成你的前端網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 暫時用記憶體存 session
sessions = {}


# 1. GET /
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Debate Master API is running.",
        "version": "1.0.0"
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

    # 如果有上傳檔案，就把內容讀進來
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

# 模擬 AI 回傳
async def fake_ai_generator(session):
    prompt = session["prompt"]
    opponent_persona = session["opponent_persona"]
    max_rounds = session["max_rounds"]
    trial = session["trial"]

    for round_num in range(1, max_rounds + 1):
        await asyncio.sleep(1)
        yield {
            "type": "conversation",
            "speaker": "agent_pro",
            "round": round_num,
            "trial": trial,
            "content": f"Pro side argument for: {prompt}"
        }

        await asyncio.sleep(1)
        yield {
            "type": "conversation",
            "speaker": "agent_con",
            "round": round_num,
            "trial": trial,
            "content": f"Con side rebuttal as persona: {opponent_persona}"
        }

    await asyncio.sleep(1)
    yield {
        "type": "summary",
        "speaker": "agent_judge",
        "pros": [
            {
                "point": "Clear argument",
                "severity": "high",
                "description": "The debate had a clear supporting argument."
            }
        ],
        "cons": [
            {
                "point": "Weak evidence",
                "severity": "mid",
                "description": "Some claims need stronger support."
            }
        ],
        "improvement_tips": [
            "Use more examples.",
            "Respond directly to counterarguments."
        ]
    }


# 把資料格式轉成 SSE
def format_sse(data: dict):
    return f"event: message\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


# 3. GET /api/v1/debate/stream/{session_id}
@app.get("/api/v1/debate/stream/{session_id}")
async def stream_debate(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]

    async def event_generator():
        async for item in fake_ai_generator(session):
            yield format_sse(item)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )