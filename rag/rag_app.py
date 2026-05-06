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

load_dotenv()


STORAGE_PATH = "./rag_storage"

Settings.llm=Groq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

Settings.embed_model=HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

print("AI Model is configured")

#----Document creation#

text="""
Germany is a country in Central Europe.
The capital city is Berlin.
Germany has a population of about 84 million people.
The official language is German.
Germany is known for its engineering, cars and beer.
Famous German car brands include BMW, Mercedes and Volkswagen.
The currency is the Euro.
Germany is a member of the European Union.
The president of Germany is Frank-Walter Steinmeier.
Germany has 16 federal states called Bundesländer.
"""
#----document building#
document=Document(text=text)
print("✅ Document created!")



#Load or build the index

if os.path.exists(STORAGE_PATH):
    print("📂 Loading existing index from disk...")
    storage_context=StorageContext.from_defaults(
        persist_dir=STORAGE_PATH
    )
    index=load_index_from_storage(storage_context)
else:
     #build vector index
    print(" Building index... (takes time first time)")
    index=VectorStoreIndex.from_documents([document])
    index.storage_context.persist(persist_dir=STORAGE_PATH)
    print("✅ Index built!")


#Query engine#
query_engine=index.as_query_engine()
print("✅ Query engine ready!")
print("\n🚀 RAG App is ready! Ask questions about Germany!\n")


#Questions

while True:
    question=input("your question ?:: ")
    if(question.lower()=="quit"):
        break

    response=query_engine.query(question)
    print(f"\n Answer: {response}\n")    


print("✅ LlamaIndex imported!")
print("✅ Groq LLM imported!")
print("✅ All RAG tools ready")
print("🚀 i have build RAG")

