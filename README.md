# KENVI – PM SHRI Kendriya Vidyalaya Bolarum AI Chatbot

A web-based AI assistant for PM SHRI Kendriya Vidyalaya Bolarum, supporting interactive Q&A, web search, and school-specific queries. Built in Python with Flask and LLM/agent backend.

---

## Features

- Interactive chat UI (Flask + HTML/JS frontend)
- AI answers with web/context support (Ollama agent, DDGS search, etc.)
- Conversation memory, context-aware responses
- Ready for local, LAN, or free cloud (Render/Replit) deployment

---

## Quickstart

### 1. Clone Repo

git clone https://github.com/YOUR_GITHUB/kenvi.git
cd kenvi

text

### 2. Install Dependencies

pip install flask flask-cors requests bs4 ddgs

text
> Add other packages used in your agent.py.

### 3. Start Local Ollama (if used)

ollama serve

text

### 4. Launch Flask Server

python server.py

text

Browse to:  
[http://localhost:5000](http://localhost:5000)

---

## License

See LICENSE file for MIT terms.
