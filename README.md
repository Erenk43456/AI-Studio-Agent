# AI-Studio-Agent

> A modular, extensible AI agent framework for intelligent task routing, planning, tool execution, memory management, and AI-assisted software development.

**AI-Studio-Agent** is a Python-based desktop AI assistant framework built around a modular **multi-agent and orchestrator-driven architecture**.

The project is designed to separate **decision-making, planning, execution, memory, model integration, and user interaction** into independent components.

Instead of relying on a single monolithic agent, AI-Studio-Agent routes each request to the appropriate subsystem, creates structured execution plans when necessary, executes tasks through registered tools, and returns the resulting output to the user.

The architecture is intentionally designed to remain **modular, extensible, model-independent, and maintainable**.

---

## ✨ Highlights

* 🧠 Multi-agent architecture
* 🔀 Centralized request routing
* 📋 LLM-based task planning
* 🛠️ Dynamic tool registry
* 💻 AI-assisted development capabilities
* 💾 Persistent conversation memory
* 🧠 Project-level memory
* 🔒 Workspace-restricted file operations
* ♻️ Automatic file backups
* 🔍 Code analysis and repair tools
* 🤖 Model abstraction layer
* 🌐 API-based LLM integration
* 🖥️ PySide6 desktop application
* ⚙️ Background AI execution
* 🧪 Pytest-based testing
* 🧰 Development test infrastructure
* 📝 Structured logging
* ❌ Explicit error propagation
* 🧩 Extensible architecture

---

# 🏗️ Architecture

AI-Studio-Agent follows a layered architecture built around specialized agents, orchestrators, tools, memory components, and model abstractions.

```text
                         ┌──────────────────────┐
                         │      PySide6 GUI     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   MainOrchestrator   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    DecisionAgent     │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐       ┌─────────────┐      ┌────────────────┐
       │ Chat System │       │Memory System│      │Development     │
       │             │       │             │      │System          │
       └──────┬──────┘       └─────────────┘      └───────┬────────┘
              │                                            │
              ▼                                            ▼
       ┌─────────────┐                            ┌────────────────┐
       │  ChatAgent  │                            │ PlannerAgent   │
       └──────┬──────┘                            └───────┬────────┘
              │                                           │
              ▼                              ┌────────────┼────────────┐
             LLM                             ▼            ▼            ▼
                                          File Tool   Code Agent   Analysis
                                                                    Tools
```

### Request Execution Pipeline

```text
User Request
     │
     ▼
MainOrchestrator
     │
     ▼
DecisionAgent
     │
     ▼
System Selection
     │
     ├──────────────┬───────────────┐
     ▼              ▼               ▼
   Chat           Memory       Development
                                    │
                                    ▼
                                PlannerAgent
                                    │
                                    ▼
                              Structured Plan
                                    │
                                    ▼
                              Tool / Agent
                                Execution
                                    │
                                    ▼
                              Structured Result
                                    │
                                    ▼
                              User Interface
```

This separation allows individual components to evolve independently without requiring the entire application to be rewritten.

---

# 🧠 Core Systems

## Main Orchestrator

The `MainOrchestrator` acts as the central coordination layer.

Its responsibilities include:

* Receiving user requests
* Invoking the decision system
* Selecting the appropriate subsystem
* Passing request context
* Executing the selected workflow
* Returning the final result

Conceptually:

```text
User
 │
 ▼
MainOrchestrator
 │
 ▼
DecisionAgent
 │
 ├── Chat
 ├── Memory
 └── Development
```

This prevents high-level application flow from becoming tightly coupled to individual agents.

---

## Decision Agent

The `DecisionAgent` determines which subsystem should handle a request.

For example:

```text
"What is Python?"
        │
        ▼
      Chat
```

```text
"Create a file called test.txt"
        │
        ▼
   Development
```

```text
"Remember that my project uses Python 3.12"
        │
        ▼
      Memory
```

The decision layer provides a clear extension point for introducing additional systems in the future.

---

# 🛠️ Development System

The Development System handles programming, file manipulation, analysis, and development-oriented workflows.

Its core components include:

```text
DevelopmentOrchestrator
        │
        ├── PlannerAgent
        │
        ├── CodeAgent
        │
        ├── Repository Analyzer
        │
        └── Tool Registry
```

### Development Execution Flow

```text
User Request
      │
      ▼
DevelopmentOrchestrator
      │
      ▼
PlannerAgent
      │
      ▼
Structured Plan
      │
      ├───────────────┐
      │               │
      ▼               ▼
  Tool Execution    CodeAgent
      │               │
      ▼               ▼
 File / Analysis    Code Tasks
      │               │
      └───────┬───────┘
              ▼
           Results
```

The orchestrator is responsible for executing the generated plan and propagating failures instead of blindly reporting every execution as successful.

---

# 📋 LLM-Based Planning

Natural-language development requests can be converted into structured execution plans.

For example:

```text
test.txt dosyası oluştur içine merhaba yaz
```

can become:

```json
{
    "steps": [
        {
            "tool": "file",
            "action": "write",
            "filename": "test.txt",
            "content": "merhaba"
        }
    ]
}
```

The orchestrator then resolves the requested tool through the tool registry and executes the operation.

This creates a clear separation between:

```text
Reasoning
   ↓
Planning
   ↓
Execution
```

The LLM does not directly control the application infrastructure. Instead, it produces a structured plan that the application validates and executes.

---

# 🔧 Tool System

AI-Studio-Agent exposes capabilities through a centralized tool registry.

Current tools include:

| Tool            | Purpose                          |
| --------------- | -------------------------------- |
| `calculator`    | Mathematical operations          |
| `file`          | Workspace file operations        |
| `code_writer`   | Code generation and modification |
| `code_analyzer` | Code analysis                    |
| `code_repair`   | Code repair                      |

Tools follow a common execution model and are registered centrally.

```text
Agent
  │
  ▼
Tool Registry
  │
  ▼
Requested Tool
  │
  ▼
execute(...)
  │
  ▼
Result
```

This allows new capabilities to be introduced without tightly coupling agents to individual tool implementations.

---

# 🔒 Workspace Security

File operations are restricted to a configured workspace boundary.

The file system tool prevents normal operations from escaping the allowed workspace.

For example, an attempt to access:

```text
C:\Windows\System32
```

is rejected when it falls outside the configured workspace.

This provides an explicit filesystem boundary between AI-generated operations and the host operating system.

The goal is to ensure that development tools operate within a controlled environment rather than having unrestricted filesystem access.

---

# ♻️ File Backup System

File modifications can automatically create backups before overwriting existing files.

Example:

```text
test.txt
test.txt.backup_<identifier>
```

This provides a basic recovery mechanism for AI-generated modifications and reduces the risk of accidental data loss.

---

# 💬 Conversation System

The framework maintains persistent conversation history.

Each conversation entry contains:

```json
{
    "user": "...",
    "assistant": "...",
    "time": "..."
}
```

The system keeps a configurable recent history window rather than allowing conversation storage to grow indefinitely.

Recent conversation context can then be supplied to the Chat Agent.

---

# 🧠 Memory Architecture

AI-Studio-Agent separates contextual information into different memory layers.

```text
                    Memory
                      │
          ┌───────────┴───────────┐
          │                       │
   Conversation Memory      Project Memory
          │                       │
          ▼                       ▼
    Recent Context          Project Context
```

### Conversation Memory

Stores recent user/assistant interactions.

### General Memory

Stores persistent information that can be recalled by agents.

### Project Memory

Stores project-specific information that can be used during development workflows.

This separation allows conversational context and development context to evolve independently.

---

# 🤖 LLM Architecture

Agents interact with language models through an abstraction layer.

Conceptually:

```text
DecisionAgent ──► Decision LLM

PlannerAgent  ──► Planner LLM

CodeAgent     ──► Code LLM

ChatAgent     ──► Chat LLM
```

Each agent can therefore have its own LLM dependency.

The current development configuration uses the same model for multiple agents to simplify development and maintain consistency.

The architecture itself supports assigning different models to different workloads.

For example:

```text
Decision Agent → Fast model
Planner Agent  → Reasoning model
Code Agent     → Coding model
Chat Agent     → General-purpose model
```

This allows model specialization to be introduced without redesigning the agent architecture.

---

# 🌐 LLM Provider Abstraction

The project contains an abstraction layer between agents and provider-specific LLM implementations.

The current development environment uses **NVIDIA NIM** with:

```text
openai/gpt-oss-20b
```

The provider abstraction is intended to support future integrations such as:

* Local LLMs
* Other API providers
* Different models per agent
* Custom inference backends
* Hybrid local/API configurations

The core agent architecture is therefore not tied to a single model provider.

---

# 🖥️ Desktop Application

The graphical interface is built using **PySide6**.

The application provides:

* Conversational interaction
* Message history
* Chat management
* AI status indicators
* Background task execution
* Persistent conversations
* Development task execution

Long-running LLM operations are handled through a worker thread to keep the GUI responsive.

```text
GUI
 │
 ▼
AIWorker
 │
 ▼
MainOrchestrator
 │
 ▼
Agents / Tools / LLM
```

---

# 🧵 Background Execution

AI operations are executed outside the main GUI thread.

This prevents long-running operations such as:

* LLM requests
* Planning
* File operations
* Code analysis

from blocking the user interface.

The worker communicates results back to the GUI through Qt signals.

---

# 🧪 Testing

The project includes both **automated testing with pytest** and a dedicated **development testing workflow**.

### Pytest

Pytest is used for automated component-level testing and regression testing.

Example:

```bash
pytest
```

### Development Testing

The project also contains development-oriented test infrastructure for validating integrated application workflows.

This is used to test interactions between components such as:

```text
User Request
      ↓
Decision
      ↓
Orchestrator
      ↓
Planner
      ↓
Tool
      ↓
Result
```

The combination of automated tests and development testing helps identify both isolated component failures and integration-level problems.

---

# 📁 Project Structure

```text
AI-Studio-Agent/
│
├── agents/
│   ├── base_agent.py
│   ├── chat_agent.py
│   ├── decision_agent.py
│   ├── planner_agent.py
│   ├── tool_agent.py
│   └── code_agent.py
│
├── app/
│   ├── core/
│   │   ├── orchestrators/
│   │   │   ├── main_orchestrator.py
│   │   │   ├── chat_orchestrator.py
│   │   │   └── development_orchestrator.py
│   │   │
│   │   └── logger.py
│   │
│   ├── window/
│   │   └── chat_controller.py
│   │
│   ├── worker.py
│   └── gui.py
│
├── memory/
│   ├── memory.py
│   ├── conversation.py
│   └── chat_manager.py
│
├── models/
│   ├── llm.py
│   ├── api_llm.py
│   └── llm_provider.py
│
├── tools/
│   ├── calculator.py
│   ├── file_tool.py
│   ├── tool_registry.py
│   ├── code_writer.py
│   ├── code_analyzer.py
│   └── code_repair.py
│
├── tests/
│
├── devtest/
│
├── data/
│
├── requirements.txt
├── main.py
└── README.md
```

> The exact project structure may evolve as the architecture is refined.

---

# ⚙️ Installation

## Requirements

* Python 3.12+
* Windows, Linux, or macOS
* Internet connection for API-based LLM providers
* NVIDIA NIM API credentials for the current API configuration

## Clone the Repository

```bash
git clone https://github.com/Erenk43456/AI-Studio-Agent.git
cd AI-Studio-Agent
```

## Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```powershell
venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

Configure the required LLM provider credentials according to the project's configuration.

---

# ▶️ Running the Application

Launch the desktop application with:

```bash
python -m app.gui
```

---

# 🧪 Running Tests

Run the automated test suite with:

```bash
pytest
```

Development-specific tests can be executed using the project's development testing workflow.

---

# 💡 Example Usage

### Create a File

```text
test.txt dosyası oluştur içine merhaba yaz
```

The request can be transformed into a structured file operation and executed through the file tool.

### Read a File

```text
test.txt dosyasını oku
```

### Development Request

```text
Bu Python dosyasındaki hatayı analiz et ve düzelt.
```

### General Conversation

```text
Python'da decorator nedir?
```

The request is routed to the appropriate subsystem based on the decision layer.

---

# 📊 Current Development Status

**Status: Active Development**

The core application architecture is operational and currently undergoing **stabilization, testing, and optimization**.

### Implemented

* [x] Modular agent architecture
* [x] Main orchestration
* [x] Decision routing
* [x] Chat system
* [x] Memory system
* [x] Development system
* [x] LLM-based planning
* [x] Tool registry
* [x] File operations
* [x] Workspace restrictions
* [x] File backup mechanism
* [x] Conversation persistence
* [x] Project memory
* [x] API LLM integration
* [x] PySide6 desktop GUI
* [x] Background AI worker
* [x] Structured logging
* [x] Error propagation
* [x] Code-oriented tooling
* [x] Automated testing infrastructure
* [x] Development testing infrastructure

### Current Focus

The current development phase focuses on improving reliability rather than introducing major architectural changes.

Current priorities include:

* Improving planner reliability
* Reducing unnecessary LLM calls
* Improving tool validation
* Standardizing tool responses
* Improving error propagation
* Optimizing context handling
* Improving code-agent reliability
* Expanding automated test coverage
* Improving response quality
* Improving system stability

The current goal is to make the existing architecture **more reliable, predictable, and efficient before introducing larger autonomous-agent capabilities.**

---

# 🔬 Engineering Approach

Development follows an incremental engineering process:

```text
Architecture
     ↓
Implementation
     ↓
Integration
     ↓
Testing
     ↓
Debugging
     ↓
Stabilization
     ↓
Optimization
     ↓
Expansion
```

Rather than continuously adding new AI capabilities, the project prioritizes making existing components reliable and predictable.

This approach allows architectural problems to be identified before the system becomes significantly more complex.

---

# 🎯 Design Principles

## Modularity

Each major responsibility is isolated into its own component.

## Separation of Concerns

Decision-making, planning, execution, memory, model integration, and presentation are separated into different layers.

## Extensibility

New agents, tools, models, and systems can be introduced without rewriting the entire application.

## Model Independence

The architecture does not depend on a specific LLM provider or model.

## Controlled Execution

LLM-generated plans are executed through application-controlled tools rather than giving the model unrestricted access to system capabilities.

## Safety

Filesystem operations are bounded by an explicit workspace.

## Maintainability

The project favors clear component boundaries and incremental development over tightly coupled implementations.

## Testability

Components and integrated workflows are designed to be testable independently.

---

# 🚀 Future Development

Potential future improvements include:

* Multi-model agent specialization
* Advanced project-level RAG
* Repository-wide code understanding
* Automated test generation
* Code verification loops
* Improved planning and replanning
* Tool result validation
* More advanced long-term memory
* Local LLM support
* Agent performance evaluation
* Automated benchmarking
* More sophisticated development workflows
* Improved autonomous task execution

These are future development directions rather than requirements of the current architecture.

---

# 🧭 Project Philosophy

AI-Studio-Agent is not intended to be simply a chatbot with a collection of tools.

The project explores how an AI system can be structured as a software platform where:

```text
Language Understanding
        ↓
Decision Making
        ↓
Planning
        ↓
Controlled Execution
        ↓
Memory
        ↓
Verification
```

can be separated into independently maintainable components.

The long-term goal is to evolve this foundation into a more capable AI-assisted development environment while maintaining control, reliability, and architectural clarity.

---

# 📌 Project Status

**Active Development**

The core system is operational and currently focused on:

> **stabilization → testing → optimization**

Major architectural expansion will follow after the existing components reach a higher level of reliability.

---

# 👨‍💻 Author

**Eren K.**

AI-Studio-Agent is an independent software engineering project focused on exploring:

* Artificial Intelligence
* Multi-Agent Systems
* LLM Engineering
* Software Architecture
* AI-Assisted Programming
* Developer Tools
* Memory Systems
* Task Planning
* Tool-Oriented AI Systems

---

## 🔗 Repository

**GitHub:**
https://github.com/Erenk43456/AI-Studio-Agent

---

## 📄 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for the full license text.