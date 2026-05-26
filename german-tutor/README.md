# 🇩🇪 Max AI — German Language Tutor

> An AI-powered German language tutor built with Python and FastAPI.
> **Live Demo:** https://max-ai-tutor.onrender.com

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat&logo=fastapi)
![Groq](https://img.shields.io/badge/Groq-LLaMA3-orange?style=flat)
![Render](https://img.shields.io/badge/Deployed-Render-purple?style=flat)

---

## ✨ Features

- 🤖 AI-powered German tutor with friendly personality
- 🧠 Conversation memory per user
- 💾 SQLite database — history saved permanently
- 🔐 Rate limiting — 10 requests per minute
- 🛡️ Input validation & sanitization
- 📊 Logging & error handling
- 🌐 Deployed live on Render.com

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI |
| AI Model | Groq API, LLaMA 3.3 70B |
| Database | SQLite, SQLAlchemy |
| Security | SlowAPI rate limiting |
| Frontend | HTML, CSS, JavaScript |
| Logging | Python logging module |
| Deploy | Render.com |

## 🚀 Quick Start

```bash
# Clone repo
git clone https://github.com/sandeepkumarnayak2-del/ai_agent/max-ai-tutor

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Run server
uvicorn server:app --reload

# Open browser
http://localhost:8000  -> https://ai-agent-maxv2.onrender.com/
```

## 📁 Project Structure
