# ShawnAI 🤖

A locally hosted AI agent built using **Python, Streamlit, Ollama, and SQLite**.

ShawnAI provides an interactive AI chat experience with persistent conversation storage, chat management, and conversation export functionality.

## ✨ Features

- **AI-Powered Conversations:** Generate responses using a locally hosted LLM through Ollama.
- **Persistent Chat History:** Store conversations using SQLite.
- **Conversation Management:** Create, search, switch between, and delete conversations.
- **Chat Export:** Export individual conversations as TXT or JSON.
- **Full Backup:** Export all conversations as a JSON backup.
- **Streaming Responses:** Display AI responses as they are generated.
- **Modern UI:** A custom dark-themed interface with a navy-and-cyan visual design.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | User interface |
| Ollama | Local LLM integration |
| Llama 3.2 (1B) | Language model |
| SQLite | Persistent database |
| JSON | Conversation export |

## 📁 Project Structure

```text
ShawnAI/
│
├── main.py
├── database.py
├── README.md
├── requirements.txt
├── .gitignore
└── screenshots/
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ShawnAI.git
cd ShawnAI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and configure Ollama

Download Ollama from:

https://ollama.com/

Pull the required model:

```bash
ollama pull llama3.2:1b
```

Make sure Ollama is running before launching the application.

### 5. Run ShawnAI

```bash
streamlit run main.py
```

The application will open in your browser.

## 💾 Data Storage

ShawnAI uses SQLite to persist conversations and messages locally. The database is created and managed by the application.

## 🚀 Future Improvements

- Support for multiple AI models
- Document-based question answering
- Improved chat customization
- Cloud deployment with a remotely accessible LLM backend

## 👨‍💻 Author

Developed as part of an internship project.

**ShawnAI — Your Local AI Chat Companion.**
