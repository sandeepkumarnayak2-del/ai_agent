from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os
import shutil

from llama_index.core import(
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage
)

from llama_index.core.readers import SimpleDirectoryReader
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from dotenv import load_dotenv

load_dotenv()

#setup
app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

Settings.llm = Groq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Storage
UPLOAD_DIR = "./uploads"
STORAGE_DIR = "./storage"
os.makedirs(UPLOAD_DIR,exist_ok=True)
os.makedirs(STORAGE_DIR,exist_ok=True)

#global index
curr_index=None


#Models classes
class QuestionRequest(BaseModel):
    question:str

class AnswerResponse(BaseModel):
    answer:str   
    status:str 

@app.get("/",response_class=HTMLResponse)
def home():
    with open("index.html","r") as f:
        return f.read()

@app.post("/upload")
def uploadfile(file:UploadFile=File(...)):
    global curr_index

    try:
        file_path=f"{UPLOAD_DIR}/{file.filename}"
        with open(file_path,"wb") as f:
            shutil.copyfileobj(file.file,f)

        print(f"file copied and saved: {file.filename}")  

        #build index
        documents=SimpleDirectoryReader(
            input_files=[file_path]
            ).load_data()
        
        print(f"pdf read done: {len(documents)} pages")

        curr_index=VectorStoreIndex.from_documents(documents)
        print(f"index build")

        return {
            "message":f"{file.filename} uploaded successfully",
            "pages":len(documents),
            "status":"ready"
        }
    except Exception as e:
        print(f"Error : {str(e)}")
        return {
            "message": f"Error: {str(e)}",
            "status": "error"
        }

@app.post("/ask",response_model=AnswerResponse)
def ask_questions(request:QuestionRequest):
    global curr_index

    try:
        if not curr_index:
            return AnswerResponse(
                answer="Upload a file first",
                status="error"
            )
        
        query_engine=curr_index.as_query_engine(
            similarity_top_k=3
        )

        response=query_engine.query(request.question)

        return AnswerResponse(
            answer=str(response),
            status="ok"
        )
    except Exception as e:
        return AnswerResponse(
            answer=f"Error: {str(e)}",
            status="error"
        )

@app.get("/status")    
def app_status():
    return {
        "status": "running",
        "document_loaded": curr_index is not None
    }   