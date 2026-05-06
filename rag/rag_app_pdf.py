from llama_index.core import (
    VectorStoreIndex, 
    Document,
    StorageContext, 
    load_index_from_storage
    )
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from dotenv import load_dotenv
import os
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core import PromptTemplate

load_dotenv()

STORAGE_PATH = "./cv_storage"
PDF_PATH = "./my_cv.pdf"

Settings.llm=Groq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

Settings.embed_model=HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

print("AI Model is configured")

#----Document creation#




#Load or build the index

if os.path.exists(STORAGE_PATH):
    print("📂 Loading existing index from disk...")
    storage_context=StorageContext.from_defaults(
        persist_dir=STORAGE_PATH
    )
    index=load_index_from_storage(storage_context)
    print("✅ CV loaded instantly!")
else:
    print("📄 Reading your CV...")
    documents=SimpleDirectoryReader(
        input_files=[PDF_PATH]
    ).load_data()
    print(f"✅ CV read! {len(documents)} pages found")

  

    print(" Building index... (takes time first time)")
    index=VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=STORAGE_PATH)
    print("✅ Index built!")


prompt = PromptTemplate(
    """You are a professional career coach analyzing a CV.
    
Context from CV:
{context_str}

Question: {query_str}

Answer professionally and specifically.
If asked for a summary, be concise and impressive.
If asked about skills, list them clearly.
If information is not in the CV, say so honestly."""
)

#Query engine#
#query_engine=index.as_query_engine()

query_engine = index.as_query_engine(
    text_qa_template=prompt,
    similarity_top_k=3
)

print("✅ Query engine for cv is ready!")


#Questions
print("\n" + "═" * 40)
print("   📄 Chat with your CV!")
print("═" * 40)
print("Ask anything about your experience!")
print("Type 'quit' to exit\n")

while True:
    question=input("your question ?:: ")
    if(question.lower()=="quit"):
        break

    response=query_engine.query(question)
    print(f"\n Answer: {response}\n")    


