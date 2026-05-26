# 📚 DocChat AI — Chat With Any PDF

> Upload any PDF and ask questions about it using AI.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat&logo=fastapi)
![LlamaIndex](https://img.shields.io/badge/LlamaIndex-RAG-orange?style=flat)
![Render](https://img.shields.io/badge/Deployed-Render-purple?style=flat)

---

## ✨ Features

- 📄 Upload any PDF document
- 🤖 Ask questions in natural language
- 🧠 RAG — answers from YOUR document
- ⚡ Fast responses with Groq AI
- 💎 Premium dark UI
- 🌐 Deployed live on Render.com

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI |
| AI Model | Groq API, LLaMA 3.3 70B |
| RAG | LlamaIndex, HuggingFace Embeddings |
| Vector DB | In-memory index |
| Frontend | HTML, CSS, JavaScript |
| Deploy | Render.com |

## 🚀 Quick Start

```bash
# Clone repo
git clone https://github.com/sandeepkumarnayak2-del/ai_agent/rag

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your GROQ_API_KEY

# Run server
uvicorn server:app --reload

# Open browser
http://localhost:8000
```
