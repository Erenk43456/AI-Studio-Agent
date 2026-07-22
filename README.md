# AI-Studio-Agent 🤖

> A modular local AI agent framework combining LLM reasoning, task planning, memory management, and tool execution.

AI-Studio-Agent is a **Local-First AI assistant framework** developed in Python.

The project combines:

- Specialized AI agents
- Local Large Language Models (LLMs)
- Persistent memory
- Tool execution
- Modern desktop interface

to create a privacy-focused AI assistant that runs entirely on the user's machine.

Unlike cloud-based AI services, conversations, memory data, and processing remain local.

---

# ✨ Features

- 🤖 Local LLM Support (Ollama + Qwen2.5)
- 🧠 Intelligent Planner Agent
- 🛠 Dynamic Tool Execution System
- 💬 Natural Language Chat Agent
- 💾 Persistent Memory System
- 📝 Conversation History Management
- 🔌 Modular Tool Registry Architecture
- 🧮 Calculator Tool
- 📁 File Management Tool
- 🖥 Modern Desktop GUI with PySide6
- ⚡ Background Processing Support
- 🧪 Automated Testing with Pytest
- 📦 Windows Executable Support
- 🔒 Local-First Privacy Architecture
- 📋 JSON-Based Task Planning

---

# 🏗 Architecture

```text
                         User
                           |
                           ▼
                    PySide6 Desktop GUI
                           |
                           ▼
                    Planner Agent
                           |
              ┌────────────┴────────────┐
              ▼                         ▼
        Tool Agent                 Chat Agent
              |
      ┌───────┼──────────┐
      ▼       ▼          ▼
  Memory  Calculator  File Tool
      |
      ▼
 Local JSON Storage


Chat Agent
      |
      ▼
 Ollama + Qwen2.5 Local LLM
```

---

# 🧠 Agent System

## Planner Agent

The Planner Agent analyzes user requests and creates structured execution plans.

Responsibilities:

- Understand user intent
- Select appropriate tools
- Generate JSON-based plans
- Route tasks between agents

Example:

```json
{
  "tool": "calculator",
  "operation": "add",
  "numbers": [20, 30]
}
```

---

## Tool Agent

The Tool Agent executes actions selected by the Planner Agent.

Supported tools:

- Calculator
- Memory
- File Operations

The modular architecture allows adding new tools easily.

---

## Chat Agent

The Chat Agent handles general conversations using a local Large Language Model.

Powered by:

- Ollama
- Qwen2.5

---

# 🛠 Technologies

- Python 3.12+
- PySide6
- Ollama
- Qwen2.5 Local LLM
- Requests
- JSON Storage
- Pytest
- PyInstaller

---

# 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/Erenk43456/AI-Studio-Agent.git
```

Navigate into the project:

```bash
cd AI-Studio-Agent
```

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🤖 Local LLM Setup

AI-Studio-Agent uses Ollama for local AI inference.

Install Qwen2.5:

```bash
ollama pull qwen2.5:3b
```

Start Ollama:

```bash
ollama serve
```

---

# ▶ Running the Application

Start the desktop application:

```bash
python -m app.gui
```

Example:

```
User:
20 ile 40'ı topla


AI:
60
```

---

# 💾 Memory System Example

Save information:

```
User:
Benim adım Eren.
```

AI:

```
Bilgi kaydedildi.
```

Later:

```
User:
Benim adım ne?
```

AI:

```
Eren
```

---

# 📦 Building Windows Executable

The project supports standalone Windows executable builds using PyInstaller.

Install PyInstaller:

```bash
pip install pyinstaller
```

Build:

```bash
pyinstaller AI-Studio-Agent.spec
```

Output:

```
dist/
 └── AI-Studio-Agent.exe
```

The generated executable runs independently.

Requirements:

- Ollama installed
- Qwen2.5 model downloaded

---

# 🧪 Running Tests

Run:

```bash
pytest
```

Example:

```
3 passed
```

Current tests:

- Calculator Tool
- Memory System

---

# 🔒 Privacy

AI-Studio-Agent follows a Local-First architecture.

Stored locally:

```
data/memory.json
data/conversation.json
```

Excluded from Git:

```
data/*.json
```

No user data is uploaded to external servers.

---

# 🛣 Roadmap

Future improvements:

- RAG Integration
- Web Search Tool
- Plugin System
- Multi-Agent Collaboration
- Advanced Long-Term Memory
- Automatic Memory Extraction
- Semantic Search
- Embedding Support
- Vector Database Integration
- Voice Assistant
- Model Switching
- API Support
- Cross Platform Support

---

# 🎯 Project Vision

The goal of AI-Studio-Agent is to evolve into a complete local AI ecosystem.

A system where specialized agents can:

- Understand tasks
- Plan actions
- Use external tools
- Maintain long-term memory
- Collaborate with other agents

while keeping user data private and local.

---

# 📄 License

This project is released under the MIT License.

---

# 👨‍💻 Author

Developed by **Eren K.**

GitHub:

https://github.com/Erenk43456