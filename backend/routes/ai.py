# routes/ai.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import get_current_user, User
from LLMs.tosreport import analyze_tos
from LLMs.tostranslate import translate_tos
from LLMs.toschat import create_chat, ask

ai_router = APIRouter()

# Store chat sessions in memory keyed by user id
# Each entry: { "chat": <Gemini chat session> }
_chat_sessions: dict = {}


# ── Request bodies ─────────────────────────────────────────────────────────────

class TosRequest(BaseModel):
    tos_text: str

class ChatRequest(BaseModel):
    message: str
    tos_text: str | None = None  # Required only on the FIRST message of a session


# ── Routes ─────────────────────────────────────────────────────────────────────

@ai_router.post("/report")
def get_report(body: TosRequest, current_user: User = Depends(get_current_user)):
    """Analyze submitted ToS text and return a structured report with scores."""
    try:
        result = analyze_tos(body.tos_text)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"report": result}


@ai_router.post("/translate")
def get_translate(body: TosRequest, current_user: User = Depends(get_current_user)):
    """Return a brainrot-flavored red flag summary of the submitted ToS text."""
    try:
        result = translate_tos(body.tos_text)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"translation": result}


@ai_router.post("/chat")
def chat(body: ChatRequest, current_user: User = Depends(get_current_user)):
    """
    Send a question about a ToS and get a response.
    
    - First message: include `tos_text` to initialize the session.
    - Subsequent messages: omit `tos_text` (session is already loaded).
    - Maintains conversation history per authenticated user.
    """
    user_id = current_user.id

    if user_id not in _chat_sessions:
        if not body.tos_text:
            raise HTTPException(
                status_code=400,
                detail="tos_text is required to start a new chat session."
            )
        try:
            _chat_sessions[user_id] = create_chat(body.tos_text)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    session = _chat_sessions[user_id]
    answer = ask(session, body.message)
    return {"response": answer}


@ai_router.post("/chat/reset")
def reset_chat(current_user: User = Depends(get_current_user)):
    """Reset the chat session for the current user."""
    _chat_sessions.pop(current_user.id, None)
    return {"status": "Chat session reset."}
