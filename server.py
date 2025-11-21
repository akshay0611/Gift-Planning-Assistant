"""
FastAPI bridge that exposes the Gift Planning Assistant over HTTP.

This file is used both for local testing and Cloud Run deployment.
It spins up a Runner around the ADK root agent and provides `/chat`
and `/health` endpoints.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import (
    InMemoryCredentialService,
)
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from adk_app.agent import root_agent

APP_NAME = "gift_planning_assistant"
DEFAULT_USER_ID = "demo-user"
DEFAULT_SESSION_ID = "default-session"
WEBUI_BUILD_DIR = Path(__file__).parent / "webui" / "build"

session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
memory_service = InMemoryMemoryService()
credential_service = InMemoryCredentialService()

runner = Runner(
    app_name=APP_NAME,
    agent=root_agent,
    session_service=session_service,
    artifact_service=artifact_service,
    memory_service=memory_service,
    credential_service=credential_service,
)

app = FastAPI(
    title="Gift Planning Assistant API",
    description="HTTP front-end for the multi-agent gift planning assistant.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., description="Natural language message for the assistant")
    user_id: Optional[str] = Field(
        None, description="Optional logical user id (defaults to demo-user)"
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional session id to continue a conversation (defaults to default-session)",
    )


class ChatResponse(BaseModel):
    reply: str
    user_id: str
    session_id: str
    events: List[dict[str, Any]]


async def _ensure_session(user_id: str, session_id: str) -> None:
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    if session is None:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )


def _extract_text(event) -> str:
    if not event.content or not event.content.parts:
        return ""
    texts: list[str] = []
    for part in event.content.parts:
        if part.text:
            texts.append(part.text)
    return "\n".join(texts).strip()


@app.get("/health", tags=["System"])
async def health() -> dict[str, str]:
    status = "ok"
    details = (
        "SPA available"
        if WEBUI_BUILD_DIR.exists()
        else "UI build not found — only API endpoints are active"
    )
    return {"status": status, "details": details}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    user_id = request.user_id or DEFAULT_USER_ID
    session_id = request.session_id or DEFAULT_SESSION_ID

    await _ensure_session(user_id, session_id)

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=request.message)],
    )

    events_payload: List[dict[str, Any]] = []
    assistant_reply: str = ""

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
    ):
        events_payload.append(event.model_dump())
        if event.author != "user":
            text = _extract_text(event)
            if text:
                assistant_reply = text

    if not assistant_reply:
        assistant_reply = "I'm sorry, I couldn't generate a response."

    return ChatResponse(
        reply=assistant_reply,
        user_id=user_id,
        session_id=session_id,
        events=events_payload,
    )


if WEBUI_BUILD_DIR.exists():
    app.mount(
        "/",
        StaticFiles(directory=WEBUI_BUILD_DIR, html=True),
        name="webui",
    )
else:

    @app.get("/", tags=["System"])
    async def landing() -> dict[str, str]:
        return {
            "message": "Web UI build not found. Generate it via `npm run build` inside webui/.",
            "status": "degraded",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )

