# 🤖 AI Support Chatbot

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-purple)](https://python.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent AI support chatbot built with LangGraph and Google's Gemini. Features FAQ matching, image retrieval, and contextual responses with conversation memory.

## ✨ Features

- 💬 **FAQ Matching** - Intelligent question-answer retrieval
- 🖼️ **Image Support** - Visual guides for user queries
- 🧠 **Conversation Memory** - Maintains context across interactions
- 🔄 **LangGraph Workflow** - Structured AI agent pipeline
- 🚀 **FastAPI Backend** - High-performance async API
- 🤖 **Gemini AI** - Powered by Google's latest LLM

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/user-chatbot.git
   cd user-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Add your API key to `.env`

5. **Run the server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access API docs**
   
   Open [http://localhost:8000/docs](http://localhost:8000/docs)

## 📁 Project Structure

```
user-chatbot/
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│   ├── ISSUE_TEMPLATE.md
│   └── PULL_REQUEST_TEMPLATE.md
├── src/
│   ├── main.py           # FastAPI application
│   ├── agent.py          # LangGraph agent definition
│   ├── retriever.py      # FAQ matching logic
│   └── image_fetcher.py  # Image retrieval service
├── .gitignore
├── .env.example
├── requirements.txt
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
└── README.md
```

## 🔧 API Endpoints

### Health Check
```http
GET /
```

### Ask Question
```http
POST /ask
Content-Type: application/json

{
  "query": "How do I reset my password?",
  "thread_id": "user_session_123"
}
```

### Response Format

```json
{
  "success": true,
  "response": {
    "user_query": "How do I reset my password?",
    "faq_id": "faq_001",
    "image_url": "https://...",
    "llm_answer": "Click on 'Forgot Password' on the login page..."
  }
}
```

## 🔧 Configuration

### Environment Variables

```env
# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 🧠 Agent Workflow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  FAQ Search │ ──▶ │ Image Search │ ──▶ │ Generate Answer │
└─────────────┘     └──────────────┘     └─────────────────┘
```

1. **FAQ Search** - Matches user query with FAQ database
2. **Image Search** - Retrieves relevant images/screenshots
3. **Generate Answer** - Creates contextual response with Gemini

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Your Name**

- GitHub: [@yourusername](https://github.com/yourusername)

---

<p align="center">Made with ❤️ and LangGraph</p>
