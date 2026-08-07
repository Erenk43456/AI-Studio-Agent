# AI-Studio-Agent

> A modular, extensible AI agent framework for intelligent task routing, planning, tool execution, memory management, and AI-assisted software development.

**AI-Studio-Agent** is a Python-based desktop AI assistant framework built around a modular **multi-agent and orchestrator-driven architecture**.

The project separates **decision-making, planning, execution, memory, model integration, and user interaction** into independent components.

Instead of relying on a single monolithic agent, AI-Studio-Agent routes requests to the appropriate subsystem, creates structured execution plans when required, executes operations through registered tools, and returns structured results to the user.

The architecture is designed to remain **modular, extensible, model-independent, testable, and maintainable**.

---

## ✨ Features

* 🧠 Multi-agent architecture
* 🔀 Centralized request routing
* 📋 LLM-based task planning
* 🏗️ Container-based dependency composition
* 🎯 Orchestrator-driven workflows
* 🛠️ Centralized tool registry
* 💻 AI-assisted software development
* 💾 Persistent conversation memory
* 🧠 Project-oriented memory
* 🔒 Workspace-restricted filesystem operations
* ♻️ Automatic file backups
* 🔍 Code analysis and repair
* 🤖 LLM abstraction layer
* 🌐 API-based LLM integration
* 🖥️ PySide6 desktop application
* ⚙️ Background AI execution
* 🧪 Pytest-based automated testing
* 🧰 Development testing infrastructure
* 📝 Structured logging
* ❌ Explicit error propagation
* 🧩 Extensible component architecture

---

# 🏗️ Architecture

AI-Studio-Agent uses a layered architecture built around:

* **Containers** — application composition and dependency wiring
* **Orchestrators** — runtime workflow coordination
* **Agents** — specialized reasoning and execution
* **Tools** — controlled concrete capabilities
* **Memory** — persistent and contextual information
* **LLM abstractions** — provider and model independence
* **GUI** — user interaction and presentation

A key architectural principle is the separation between **composition** and **execution**.

```text
┌──────────────────────────────┐
│          PySide6 GUI         │
│                              │
│     ChatController           │
│     AIWorker                 │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      MainOrchestrator        │
│                              │
│      Request Routing         │
│      System Selection        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       DecisionAgent          │
│                              │
│    Request Classification    │
└──────────────┬───────────────┘
               │
       ┌───────┼────────┐
       │       │        │
       ▼       ▼        ▼
    Chat    Memory  Development
    System  System     System
                       │
                       ▼
              DevelopmentOrchestrator
                       │
              ┌────────┼────────┐
              │        │        │
              ▼        ▼        ▼
           Planner  CodeAgent  Tools
              │        │        │
              └────────┼────────┘
                       ▼
                  Execution
                    Results
```

---

# 🧩 Container Architecture

Containers form the **composition and dependency-wiring layer** of the application.

They construct and connect:

* Agents
* Orchestrators
* Tools
* Memory systems
* LLM instances
* Supporting services

Runtime components do not need to construct their own dependencies.

```text
                    Application Container
                             │
             ┌───────────────┼────────────────┐
             │               │                │
             ▼               ▼                ▼
      ChatContainer   MemoryContainer   DevelopmentContainer
             │               │                │
             ▼               ▼                ▼
        ChatAgent      Memory System     PlannerAgent
        ChatOrch.      Conversation      CodeAgent
        Chat LLM       Project Memory    Repository Analyzer
             │               │                │
             ▼               ▼                ▼
        Chat System     Memory System   Development System
```

This keeps **object construction** separate from **runtime business logic**.

### Development Container

The development subsystem is composed approximately as follows:

```text
DevelopmentContainer
        │
        ├── Planner LLM
        │       │
        │       ▼
        │   PlannerAgent
        │
        ├── Code LLM
        │       │
        │       ▼
        │   CodeAgent
        │
        ├── Tool Registry
        │       ├── Repository Analyzer
        │       ├── File Tool
        │       ├── Code Writer
        │       ├── Code Analyzer
        │       └── Code Repair
        │
        ├── Project Memory
        │
        └── DevelopmentOrchestrator
                ├── PlannerAgent
                ├── CodeAgent
                ├── Repository Analyzer
                └── Tool Registry
```

The `DevelopmentOrchestrator` receives these dependencies from the container instead of constructing them itself.

This keeps orchestration focused on **workflow execution** rather than application composition.

---

# 🔄 Request Execution Flow

A typical development request follows this pipeline:

```text
User Request
     │
     ▼
ChatController
     │
     ▼
AIWorker
     │
     ▼
MainOrchestrator
     │
     ▼
DecisionAgent
     │
     ▼
DevelopmentOrchestrator
     │
     ▼
PlannerAgent
     │
     ▼
Structured Execution Plan
     │
     ├─────────────────┐
     │                 │
     ▼                 ▼
Tool Registry       CodeAgent
     │                 │
 ┌───┼───────┐         │
 ▼   ▼       ▼         │
File Analyzer Repair   │
 │           │         │
 └───────────┴─────────┘
             │
             ▼
      Execution Results
             │
             ▼
      MainOrchestrator
             │
             ▼
          AIWorker
             │
             ▼
            GUI
```

The architecture separates five major responsibilities:

| Responsibility   | Description                                          |
| ---------------- | ---------------------------------------------------- |
| **Decision**     | Determines which subsystem should handle the request |
| **Planning**     | Determines which operations are required             |
| **Execution**    | Performs the requested operations                    |
| **Memory**       | Provides persistent and contextual information       |
| **Presentation** | Returns results to the user                          |

---

# 🧠 Separation of Responsibilities

| Layer                | Responsibility                               |
| -------------------- | -------------------------------------------- |
| GUI                  | User interaction and presentation            |
| Worker               | Background execution                         |
| Main Orchestrator    | Global request routing                       |
| Decision Agent       | Request classification                       |
| System Orchestrators | Subsystem workflow control                   |
| Containers           | Dependency construction and wiring           |
| Agents               | Specialized reasoning and task execution     |
| Planner              | Natural language → structured execution plan |
| Tool Registry        | Tool discovery and dispatch                  |
| Tools                | Concrete operations                          |
| Memory               | Persistent and contextual information        |
| LLM Layer            | Provider and model abstraction               |

The dependency direction is intentionally kept simple:

```text
Composition
     ↓
Containers
     ↓
Orchestration
     ↓
Agents
     ↓
Tools / Memory / LLM
```

This allows individual components to evolve without forcing unrelated parts of the system to change.

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

Examples:

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

The decision layer also provides an extension point for introducing additional systems in the future.

---

# 🛠️ Development System

The Development System handles programming, file manipulation, analysis, and development-oriented workflows.

```text
DevelopmentOrchestrator
        │
        ├── PlannerAgent
        ├── CodeAgent
        ├── Repository Analyzer
        └── Tool Registry
```

### Development Workflow

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
File / Analysis   Code Tasks
     │               │
     └───────┬───────┘
             ▼
          Results
```

The orchestrator is responsible for executing generated plans and propagating failures instead of blindly reporting every execution as successful.

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

The orchestrator resolves the requested tool through the tool registry and executes the operation.

This creates a clear separation between:

```text
Reasoning
    ↓
Planning
    ↓
Execution
```

The LLM does **not** directly control application infrastructure.

Instead, it produces a structured plan that the application can validate and execute through controlled capabilities.

---

# 🔧 Tool System

AI-Studio-Agent exposes capabilities through a centralized tool registry.

### Current Tools

| Tool            | Purpose                          |
| --------------- | -------------------------------- |
| `calculator`    | Mathematical operations          |
| `file`          | Workspace file operations        |
| `code_writer`   | Code generation and modification |
| `code_analyzer` | Code analysis                    |
| `code_repair`   | Code repair                      |

The execution model is:

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

is rejected when the target is outside the configured workspace.

This creates an explicit filesystem boundary between AI-generated operations and the host operating system.

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

A conversation entry follows the general structure:

```json
{
  "user": "...",
  "assistant": "...",
  "time": "..."
}
```

The system keeps a configurable recent-history window rather than allowing the active context to grow indefinitely.

Recent conversation context can then be supplied to the Chat Agent.

---

# 🧠 Memory Architecture

AI-Studio-Agent separates contextual information into different memory layers.

```text
                    Memory
                      │
          ┌───────────┴───────────┐
          │                       │
 Conversation Memory       Project Memory
          │                       │
          ▼                       ▼
   Recent Context           Project Context
```

### Conversation Memory

Stores recent user/assistant interactions.

### General Memory

Stores persistent information that can be recalled by agents.

### Project Memory

Stores project-specific information used during development workflows.

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

The current configuration may use the same model for multiple workloads to simplify development and maintain consistency.

The architecture supports assigning different models to different workloads:

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

The provider abstraction is intended to support:

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

Long-running AI operations are handled outside the main GUI thread to keep the interface responsive.

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

The project includes automated testing with **pytest** as well as development-oriented testing infrastructure.

## Pytest

Run the automated test suite with:

```bash
pytest
```

Pytest is used for component-level testing and regression testing.

## Development Testing

The project also contains development-oriented infrastructure for validating integrated workflows.

Typical integration flow:

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

This combination helps identify both isolated component failures and integration-level problems.

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
├── devtest/
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

Development-specific tests can be executed through the project's development testing workflow.

---

# 💡 Example Usage

## Create a File

```text
test.txt dosyası oluştur içine merhaba yaz
```

The request is converted into a structured operation and executed through the file tool.

## Read a File

```text
test.txt dosyasını oku
```

## Development Request

```text
Bu Python dosyasındaki hatayı analiz et ve düzelt.
```

## General Conversation

```text
Python'da decorator nedir?
```

Requests are routed to the appropriate subsystem through the decision layer.

---

# 📊 Development Status

**Status: Active Development**

The core application architecture is operational and currently focused on **stabilization, testing, and optimization**.

## Implemented

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

## Current Focus

The current development phase focuses on improving reliability rather than introducing major architectural changes.

Current priorities include:

* Improving planner reliability
* Reducing unnecessary LLM calls
* Improving tool validation
* Standardizing tool responses
* Improving error propagation
* Optimizing context handling
* Improving Code Agent reliability
* Expanding automated test coverage
* Improving response quality
* Improving system stability

The immediate goal is to make the existing architecture **more reliable, predictable, and efficient** before introducing larger autonomous-agent capabilities.

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

This approach helps identify architectural problems before the system becomes significantly more complex.

---

# 🎯 Design Principles

## Modularity

Each major responsibility is isolated into its own component.

## Separation of Concerns

Decision-making, planning, execution, memory, model integration, and presentation are separated into distinct layers.

## Extensibility

New agents, tools, models, and systems can be introduced without rewriting the entire application.

## Model Independence

The architecture is not fundamentally tied to a specific LLM provider or model.

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
Result Handling
        ↓
Memory
        ↓
Verification
```

can be separated into independently maintainable components.

The long-term goal is to evolve this foundation into a more capable **AI-assisted development environment** while maintaining control, reliability, and architectural clarity.

---

# 📌 Project Status

**Active Development**

The core system is operational and currently focused on:

```text
Stabilization
     ↓
Testing
     ↓
Optimization
```

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

# 🔗 Repository

[GitHub Repository](https://github.com/Erenk43456/AI-Studio-Agent)

---

# 📄 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for the full license text.
