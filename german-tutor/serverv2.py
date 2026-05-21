from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from typing import List, Optional
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import logging
import os
from contextlib import asynccontextmanager
import time
from security import sanitize_input, validate_username
from new_db import init_db, save_message, get_history, get_words

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("🚀 Max AI server started!")
    init_db()  # ← ADD THIS
    logger.info("💾 Database initialized!")
    yield
    # SHUTDOWN
    logger.info("🛑 Server shutting down")

app = FastAPI(
    title="Max AI German Tutor",
    description="AI powered German tutor by Sandeep Kumar Nayak",
    version="3.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    username: str = "Guest"
    history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
    reply: str
    status: str


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    logger.info(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    duration = round(time.time() - start, 3)
    logger.info(f"📤 {response.status_code} | {duration}s")
    return response

@app.get("/", response_class=HTMLResponse)
def home():
    with open("indexv2.html", "r") as f:
        return f.read()


@app.get("/status")
def status():
    return {
        "app": "Max AI German Tutor",
        "status": "running",
        "version": "3.0",
        "built_by": "Sandeep Kumar Nayak",
        "time": datetime.now().strftime("%H:%M")
    }

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    
    try:
        # Validate input
        if not chat_request.message.strip():
            return ChatResponse(
                reply="Please type a message!",
                status="error"
            )
        if len(chat_request.message) > 1000:
            return ChatResponse(
                reply="Message too long! Max 1000 characters.",
                status="error"
            )
        # Validate username
        if not validate_username(chat_request.username):
            chat_request.username = "Guest"

        # Sanitize input
        clean_message = sanitize_input(chat_request.message)
        logger.info(f"👤 {chat_request.username}: {clean_message[:50]}")

        logger.info(f" {chat_request.username}: {chat_request.message[:50]}")

        # Build conversation for max
        messages = [
            {
                "role": "system",
                "content": f"""You are Max, a friendly German tutor.
                Student: {chat_request.username}
                Teach German in a fun encouraging way.
                Always include example sentences.
                End with a question or exercise. 😊"""
            }
        ]
        for msg in chat_request.history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
            # Add new message
        messages.append({
            "role": "user",
            "content": clean_message
        })

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1000
        )
        reply = response.choices[0].message.content
        logger.info(f"🤖 Max replied to {chat_request.username}")
        # SAVE TO DATABASE ← ADD THESE
        save_message(chat_request.username, "user", clean_message)
        save_message(chat_request.username, "assistant", reply)
        logger.info(f"💾 Messages saved to database!")

        return ChatResponse(reply=reply, status="ok")
    
    except RateLimitExceeded:
        logger.warning(f"    Rate limit: {chat_request.username}")
        return ChatResponse(
            reply="Too many messages! Please wait a minute. ⏳",
            status="error"
        )
    except Exception as e:
        logger.error(f" Error: {str(e)}")
        return ChatResponse(
            reply="Sorry, Max is having trouble. Try again! 😊",
            status="error"
        )




@app.get("/history/{username}")
def get_chat_history(username: str):
    try:
        history = get_history(username, limit=50)
        return {
            "username": username,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": str(msg.timestamp)
                }
                for msg in history
            ],
            "total": len(history)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/words/{username}")
def get_word_bank(username: str):
    try:
        words = get_words(username)
        return {
            "username": username,
            "words": words,
            "count": len(words)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/stats/{username}")
def get_stats(username: str):
    try:
        history = get_history(username, limit=1000)
        words = get_words(username)
        return {
            "username": username,
            "total_messages": len(history),
            "words_learned": len(words),
            "word_list": words
        }
    except Exception as e:
        return {"error": str(e)}

@app.delete("/history/{username}")
def clear_history(username: str):
    try:
        from new_db import SessionLocal, Conversation
        db = SessionLocal()
        db.query(Conversation)\
            .filter(Conversation.username == username)\
            .delete()
        db.commit()
        db.close()
        return {"message": f"History cleared for {username}"}
    except Exception as e:
        return {"error": str(e)}