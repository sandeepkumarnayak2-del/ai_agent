from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List,Optional
from groq import Groq
from dotenv import load_dotenv
import os


load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r") as f:
        return f.read()

@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Hello {name}!", "from": "Max AI Server"}

@app.get("/ask/{question}")
def germantutor(question:str):
    response=client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role":"system","content":"You are Max, a helpful German tutor"},
            {"role": "user", "content": question}
        ]
    )    

    return {
        "question":question,
        "answer":response.choices[0].message.content,
        "status":"ok"
    }


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
    history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
    reply: str
    status: str    

@app.get("/app2")
def home():
    return{
        "app": "Max AI German Tutor",
        "status": "running",
        "version": "2.0"
    }

@app.post("/chat",response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        #Building conversation
        messages=[
            {
                "role": "system",
                "content": """You are Max, a friendly German tutor.
                Teach German in a fun encouraging way.
                Always include example sentences.
                End with a question or exercise."""

            }
        ]

        for msg in request.history:
            messages.append({
                "role":msg.role,
                "content":msg.content
            })

        #add the new message
        messages.append({
            "role":"user",
            "content":request.message
        })    


        # Call AI
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )

        reply = response.choices[0].message.content
        return ChatResponse(reply=reply, status="ok")

    except Exception as e:
        print("❌ ERROR:", str(e))  # See exact error in terminal
        return ChatResponse(reply=f"Error: {str(e)}", status="error")

