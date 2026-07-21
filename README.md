# AI-Studio-Agent 🤖

A modular **Local LLM powered AI Agent framework** built with Python.

AI-Studio-Agent is a personal AI assistant infrastructure designed with an agent-based architecture. It combines local language models, task planning, tool execution, and persistent memory to create an extensible AI system.

The project focuses on building a lightweight and customizable AI agent architecture that can operate locally while maintaining user data privacy.

---

# 🚀 Features

- Local LLM integration with Ollama
- Agent-based architecture
- Task planning with Planner Agent
- Tool execution with Tool Agent
- Persistent memory system
- Conversation history storage
- Modular tool registry
- Calculator operations
- File operation support
- Extensible architecture for adding new capabilities

---

# 🏗️ Architecture

```
User
 |
 v
Main Application
 |
 v
Planner Agent
 |
 v
Tool Agent
 |
 +----------------+
 |                |
 v                v
Memory Tool    Calculator
 |
 v
JSON Storage
```

The system separates decision-making, execution, and memory management into independent modules.

---

# 📂 Project Structure

```
AI-Studio-Agent

├── agents
│   ├── base_agent.py
│   ├── planner_agent.py
│   └── tool_agent.py
│
├── memory
│   ├── memory.py
│   └── conversation.py
│
├── models
│   └── llm.py
│
├── tools
│   ├── calculator.py
│   ├── file_tool.py
│   ├── memory_tool.py
│   └── tool_registry.py
│
├── main.py
└── README.md
```

---

# 🛠️ Technologies

- Python 3.12+
- Ollama
- Qwen2.5 Local LLM
- Requests
- JSON-based storage
- Object-Oriented Programming (OOP)

---

# ⚙️ Installation

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

Activate the environment:

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🧠 Local LLM Setup

Install Ollama and download the model:

```bash
ollama pull qwen2.5:1.5b
```

Run the model:

```bash
ollama run qwen2.5:1.5b
```

---

# ▶️ Usage

Start the application:

```bash
python main.py
```

Example:

```
Input:
Benim adım Eren

Output:
isim kaydedildi.
```

```
Input:
Benim adım ne?

Output:
eren
```

```
Input:
20 ile 40'ı topla

Output:
60
```

---

# 🔮 Future Improvements

- Advanced natural language response generation
- Automatic tool discovery system
- Web search integration
- Code execution capabilities
- Web-based user interface
- Improved long-term memory system
- Agent self-evaluation and replanning
- More advanced AI workflows

---

# 🎯 Project Goal

The goal of AI-Studio-Agent is to explore and develop a scalable AI agent architecture using local language models.

The project aims to create a privacy-focused, customizable, and extensible AI assistant framework that can be expanded with new tools and capabilities.

---

# 👨‍💻 Developer

Eren

GitHub:
https://github.com/Erenk43456