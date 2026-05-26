# AI-LEARNING
# 🇩🇪 Max AI — German Tutor Agent

A personal German language tutor powered by AI.
Built in Week 1 of my AI learning journey.

## Features
- 🤖 AI-powered German tutor with personality
- 🧠 Remembers your progress between sessions
- 📚 Personal word bank
- 🔧 AI agent with tools (time, calculator, notes)
- 🎮 German quiz game

## Tech Stack
- Python
- Groq API (LLaMA 3)
- JSON for persistence

## How to Run
```bash
pip install groq
python3 max_agent.py
```

## My Journey
Built this in 7 days as a complete beginner.
Learning AI development one day at a time! 💪



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
git clone https://github.com/sandeepkumarnayak2-del/max-ai-tutor

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Run server
uvicorn server:app --reload

# Open browser
http://localhost:8000
```

## 📁 Project Structure
