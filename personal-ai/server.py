from datetime import datetime
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from langchain_groq import ChatGroq
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import TextLoader
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain


load_dotenv()

# ---- MODELS ----
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    status: str


app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---- LOAD KNOWLEDGE ----
print("📚 Loading knowledge base...")
loader = TextLoader("knowledge.txt")
documents = loader.load()


splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

chunks = splitter.split_documents(documents)
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

print("Knowledge is set and  ready!")



memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

#  RAG CHAIN 
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(
        search_kwargs={"k": 3}
    ),
    memory=memory
)


# ---- ENDPOINTS ----
@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r") as f:
        return f.read()
    

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # Check for special commands
        msg = request.message.lower()

        if "time" in msg or "date" in msg:
            now = datetime.now().strftime("%A, %B %d %Y, %H:%M")
            extra = f"\n\n[Current time: {now}]"
        else:
            extra = ""

        result = qa_chain.invoke({
            "question": request.message + extra
        })

        return ChatResponse(
            reply=result["answer"],
            status="ok"
        )

    except Exception as e:
        print(f" Error: {str(e)}")
        return ChatResponse(
            reply=f" something went wrong: {str(e)}",
            status="error"
        )    


@app.get("/status")
def getstatus():
    return {
        "status":"running",
        "knowledge": "Sandeep Kumar Nayak",
        "time": datetime.now().strftime("%H:%M")
    }
