# AI-Studio-Agent 🤖

> **A modular desktop AI assistant powered by local LLMs, intelligent agents, persistent memory, and tool execution.**

AI-Studio-Agent is a modular AI assistant framework developed in Python.

The project combines multiple autonomous agents, persistent memory, local Large Language Models (LLMs), and a modern desktop interface to provide a fully local and privacy-focused AI assistant.

Unlike cloud-based AI services, all conversations, memory, and user data remain on the user's machine.

---

# ✨ Features

- 🤖 Local LLM Support (Ollama + Qwen2.5)
- 🧠 Planner Agent for intelligent task analysis
- 🛠 Tool Agent for dynamic tool execution
- 💬 Chat Agent for natural language conversations
- 💾 Persistent Memory System
- 📝 Conversation History Management
- 🔌 Modular Tool Registry Architecture
- 🧮 Calculator Tool
- 📁 File Management Tool
- 🖥 Modern Desktop GUI (PySide6)
- ⚡ Background Processing using QThread
- 🧪 Automated Testing with Pytest
- 📦 Windows Executable Support
- 🔒 Fully Local & Privacy Focused

---

# 🏗 Architecture

```text
                User
                  │
                  ▼
          Desktop Interface
                  │
                  ▼
           Planner Agent
          ┌───────┴────────┐
          ▼                ▼
     Tool Agent      Chat Agent
          │
   ┌──────┼────────────┐
   ▼      ▼            ▼
Memory  Calculator   File Tool
```

---

# 🧠 Agent Overview

## Planner Agent

The Planner Agent analyzes the user's request and determines the most appropriate action.

Responsibilities:

- Analyze user requests
- Select the appropriate tool or agent
- Generate structured execution plans

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

The Tool Agent executes the selected tools.

Currently supported tools:

- Calculator
- Memory
- File Operations

---

## Chat Agent

The Chat Agent handles normal conversations using a local Large Language Model.

---

# 🛠 Technologies

- Python 3.12+
- PySide6
- Ollama
- Qwen2.5 Local LLM
- Requests
- JSON
- Pytest
- PyInstaller

---

# 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/Erenk43456/AI-Studio-Agent.git
```

Navigate to the project directory:

```bash
cd AI-Studio-Agent
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

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

AI-Studio-Agent uses Ollama for local inference.

Download the model:

```bash
ollama pull qwen2.5:3b
```

Start the Ollama server:

```bash
ollama serve
```

---

# ▶ Usage

Run the desktop application:

```bash
python -m app.gui
```

Example:

```
User:
Calculate 20 + 40

AI:
60
```

Memory example:

```
User:
My name is Eren.

AI:
Information saved.
```

Later:

```
User:
What's my name?

AI:
Your name is Eren.
```

---

# 📦 Windows Executable

A standalone Windows executable is available.

```
AI-Studio-Agent.exe
```

Requirements:

- Ollama installed
- Qwen2.5 model downloaded

---

# 🧪 Running Tests

Execute all tests:

```bash
pytest
```

Example output:

```
3 passed
```

Current test coverage:

- Calculator Tool
- Memory System

---

# 🔒 Privacy

All conversations and memory are stored locally.

The following files are excluded from GitHub:

```
data/memory.json
data/conversation.json
```

No personal data is uploaded to external servers.

---

# 🛣 Roadmap

Planned features:

- RAG Integration
- Web Search Tool
- Plugin Architecture
- Multi-Agent Collaboration
- Long-Term Memory
- Voice Assistant
- Model Switching
- API Support
- Cross-Platform Support
- Optional Cloud Synchronization

---

# 🎯 Project Vision

The long-term goal of AI-Studio-Agent is to evolve into a modular AI ecosystem capable of planning tasks, interacting with external tools, managing long-term memory, and collaborating between specialized AI agents while running entirely on local hardware.

---

# 📄 License

This project is released under the MIT License.

---

# 👨‍💻 Author

Developed by **Eren K.**

GitHub:
https://github.com/Erenk43456