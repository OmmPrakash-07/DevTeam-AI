# DevTeam AI

> **Multi-Agent Autonomous Software Development Team**

DevTeam AI is an AI-powered software development platform that uses multiple specialized AI agents to transform an explicit software-development request into a working project.

Instead of relying on a single general-purpose coding agent, DevTeam AI divides the development workflow into specialized stages for requirements, architecture, implementation, file generation, testing, debugging, code review, and documentation.

---

## Current Project Status

The project has reached a functional end-to-end stage with:

- FastAPI backend
- LangGraph multi-agent workflow
- 8 specialized AI agents
- Multiple LLM provider fallback
- Ollama-first local LLM support
- Safe generated-project filesystem handling
- Automated testing and debugging loop
- AI code review
- Automatic documentation generation
- Real-time agent activity streaming
- Persistent generated-project history
- Project viewer
- Project ZIP download
- React/Vite frontend
- Sidebar navigation
- DevTeam AI/J.A.R.V.I.S. branding
- Intent-aware handling for `ANSWER`, `CODING_HELP`, and `BUILD_PROJECT`
- Frontend navigation separated into Home, New Project, My Projects, History, and Settings

The remaining major work is to connect the frontend **History** page to a persistent backend conversation-history API so normal questions and coding-help requests can be stored and displayed separately from generated projects.

---

## Product Goal

The long-term goal is to provide an autonomous software-engineering environment where a user can describe a software idea and an AI development team can collaboratively transform it into a working project.

The system is intentionally designed around specialized agents rather than one monolithic coding agent.

```text
User Request
     |
     v
Intent Classifier
     |
     +---- ANSWER ---------> Answer Response
     |
     +---- CODING_HELP -----> Coding Help Response
     |
     +---- BUILD_PROJECT ---> Multi-Agent Development Workflow
                                  |
                                  v
                              Requirements
                                  |
                                  v
                              Architecture
                                  |
                                  v
                              Development
                                  |
                                  v
                              File System
                                  |
                                  v
                                Testing
                                  |
                         +--------+--------+
                         |                 |
                      Failed            Passed
                         |                 |
                         v                 v
                      Debugger       Code Reviewer
                         |                 |
                         +----> Tester    v
                                      Documentation
                                           |
                                           v
                                          END
```

---

# Features Implemented

## 1. Multi-Agent Development Workflow

DevTeam AI currently contains eight specialized agents:

| Agent | Responsibility |
|---|---|
| Project Manager | Converts the software request into structured requirements and tasks |
| Architect | Designs the project architecture and folder structure |
| Developer | Generates source code, tests, and project documentation |
| File System Agent | Safely creates generated project files |
| Tester | Validates and executes generated tests |
| Debugger | Attempts to fix generated-project failures |
| Code Reviewer | Reviews implementation quality and consistency |
| Documentation | Generates documentation based on the generated project |

---

## 2. LangGraph Workflow

The main project-generation workflow is implemented using LangGraph.

```text
START
  |
  v
Project Manager
  |
  v
Architect
  |
  v
Developer
  |
  v
File System
  |
  v
Tester
  |
  +---- Tests Failed ----> Debugger
  |                          |
  |                          v
  |                        Tester
  |
  +---- Tests Passed ----> Code Reviewer
                               |
                               v
                         Documentation
                               |
                               v
                              END
```

The debugger loop is limited to a maximum of three debugging attempts before the workflow continues to code review.

---

# Intent-Aware AI Interaction

A major architectural improvement is that DevTeam AI is not intended to treat every user message as a project-generation request.

The system recognizes three request categories:

### `ANSWER`

For normal questions and explanations.

Examples:

```text
What is Python?
Explain REST API.
What is machine learning?
```

These should return an AI answer without creating a project folder or project record.

### `CODING_HELP`

For coding assistance that does not request a complete generated project.

Examples:

```text
Write a Python function to reverse a string.
Fix this JavaScript error.
Explain this React code.
```

These should return coding assistance without creating a generated project.

### `BUILD_PROJECT`

For explicit software-generation requests.

Examples:

```text
Build a Python calculator application.
Create a React expense tracker.
Develop a FastAPI backend for a bike rental system.
```

These enter the full multi-agent development workflow and are stored as generated projects.

---

# Project Persistence

Generated projects are persisted separately from normal AI conversations.

The backend uses SQLite through Python's standard library and a project repository service.

### Project metadata

The `projects` table stores information such as:

- Project ID
- User request
- Creation time
- Updated time
- Project status
- Test status
- File count

### Generated project files

Actual generated files are stored under:

```text
recent_projects/<project_id>/
```

This allows generated projects to be viewed again after generation.

---

# Project API

## Health Check

```http
GET /
```

Example response:

```json
{
  "message": "DevTeam AI is running"
}
```

## Generate Project

```http
POST /generate
```

Example request:

```json
{
  "request": "Create a simple Python calculator application"
}
```

## Real-Time Generation

```http
GET /generate/stream?request=<encoded-request>
```

The frontend uses Server-Sent Events to receive real-time workflow activity.

The stream can communicate events for:

- Intent detection
- Agent activity
- Project completion
- Normal AI responses
- Coding-help responses
- Errors

## Project List

```http
GET /projects
```

Returns persisted generated projects.

## Project Details

```http
GET /projects/{project_id}
```

Returns project metadata and generated files.

## Project Download

```http
GET /projects/{project_id}/download
```

Returns the generated project as a ZIP archive.

---

# Frontend

The frontend is built using:

- React
- Vite
- Tailwind CSS

The frontend currently contains:

- DevTeam AI branding
- J.A.R.V.I.S.-style logo asset
- Hamburger sidebar
- Home navigation
- New Project navigation
- My Projects navigation
- History navigation
- Settings navigation
- AI request interface
- Real-time agent activity
- Project generation result UI
- Generated project viewer
- Project ZIP download
- Persistent My Projects interface

### Navigation structure

```text
Home
 |
 +-- New Project
 |
 +-- My Projects
 |
 +-- History
 |
 +-- Settings
```

### Data separation

The intended separation is:

```text
My Projects
    |
    +-- Only generated software projects
    +-- Project request
    +-- Architecture
    +-- Generated files
    +-- Test results
    +-- Debugging information
    +-- Code review
    +-- Documentation
    +-- Project metadata
    +-- View Project
    +-- Download ZIP

History
    |
    +-- Normal questions
    +-- Explanations
    +-- Coding help
    +-- AI conversations
```

Recent Projects is no longer intended to be a permanent section of the Home dashboard. Generated projects belong in **My Projects**.

The current frontend History screen is a placeholder until the backend conversation-history persistence/API is implemented.

---

# Agent Activity Streaming

The frontend receives real-time agent activity through Server-Sent Events.

The workflow can show stages such as:

```text
Project Manager
Architect
Developer
File System
Tester
Debugger
Code Reviewer
Documentation
```

Each stage can communicate states such as:

- Pending
- Running
- Completed
- Failed

This provides live visibility into the autonomous development workflow.

---

# Testing System

The Tester agent validates generated projects.

For Python projects, the system can perform:

- Python AST validation
- Import validation
- Unit-test execution
- Suitable non-interactive module execution
- Timeout handling
- Failure detection

The default Python test command is:

```bash
python -m unittest discover -s tests
```

---

# Debugging System

If generated tests fail, the workflow can send the project back to the Debugger.

```text
Tester
  |
  | failure
  v
Debugger
  |
  v
Tester
```

The current workflow allows up to three debugging attempts.

After the debugging limit is reached, the workflow continues to code review rather than looping indefinitely.

---

# File-System Security

Generated project files are handled through a protected filesystem layer.

The filesystem implementation includes protection against:

- Absolute paths
- Path traversal
- Backslash-based traversal
- Writing outside the generated project directory
- Unsafe project-root symlinks
- Unsafe recursive reads
- Unsafe ZIP traversal

Project reads do not create missing project directories.

Symlinks are skipped when recursively reading or ZIPing generated projects.

---

# LLM Provider Architecture

The provider router supports multiple LLM providers.

The current provider sequence is designed around local Ollama first, followed by configured cloud providers.

Current supported providers include:

1. Ollama
2. Groq
3. Google Gemini
4. DeepSeek
5. Anthropic Claude
6. OpenRouter

The router can attempt another configured provider when an earlier provider is unavailable or fails.

### Local Ollama

Ollama is currently used as the preferred local provider when configured.

A supported local model in the current development environment is:

```text
GPT-OSS 20B
```

The advantage of the local provider is that development can continue without depending entirely on cloud API quota or credit availability.

---

# Technology Stack

## Backend

- Python
- FastAPI
- LangGraph
- LangChain
- python-dotenv
- SQLite
- Python subprocess
- Python AST

## Frontend

- React
- Vite
- Tailwind CSS
- Server-Sent Events

## AI

- Ollama
- Google Gemini
- Groq
- DeepSeek
- Anthropic Claude
- OpenRouter

---

# Project Structure

```text
DevTeam-AI/
|
+-- backend/
|   |
|   +-- agents/
|   |   +-- __init__.py
|   |   +-- project_manager.py
|   |   +-- architect.py
|   |   +-- developer.py
|   |   +-- filesystem_agent.py
|   |   +-- tester.py
|   |   +-- debugger.py
|   |   +-- code_reviewer.py
|   |   +-- documentation.py
|   |
|   +-- graph/
|   |   +-- __init__.py
|   |   +-- state.py
|   |   +-- workflow.py
|   |
|   +-- services/
|   |   +-- __init__.py
|   |   +-- llm.py
|   |   +-- project_repository.py
|   |
|   +-- tools/
|   |   +-- __init__.py
|   |   +-- filesystem.py
|   |
|   +-- main.py
|   +-- .env
|
+-- frontend/
|   +-- public/
|   |   +-- jarvis.png
|   |
|   +-- src/
|   |   +-- App.jsx
|   |   +-- main.jsx
|   |
|   +-- package.json
|
+-- recent_projects/
|
+-- generated_projects/
|
+-- tests/
|
+-- .gitignore
+-- README.md
```

---

# Installation

## Requirements

Install:

- Python 3.10+
- Node.js
- npm
- Git
- Ollama if using the local provider

Clone the repository:

```bash
git clone https://github.com/OmmPrakash-07/DevTeam-AI.git
```

Enter the project:

```bash
cd DevTeam-AI
```

---

# Backend Setup

Create a Python virtual environment:

```powershell
python -m venv backend/venv
```

Activate it on Windows:

```powershell
backend\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -U langchain-google-genai langgraph langchain python-dotenv fastapi uvicorn anthropic openai
```

Install/configure any additional provider packages required by the current provider implementation.

---

# Environment Configuration

Create:

```text
backend/.env
```

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

Only configure the providers you intend to use.

If Ollama is being used locally, make sure the Ollama service and required model are available.

### Security

Never commit API keys or other secrets to GitHub.

The repository should keep environment files excluded through `.gitignore`.

---

# Running the Backend

From the project root:

```powershell
cd backend
uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Running the Frontend

From another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite will display the local development URL in the terminal.

The frontend uses:

```text
VITE_API_URL
```

when configured. Otherwise it falls back to:

```text
http://127.0.0.1:8000
```

---

# Example Project Request

Example:

```text
Build a bike rental application using React, FastAPI and PostgreSQL.
```

The intended workflow is:

```text
User Request
    ↓
Intent Detection
    ↓
BUILD_PROJECT
    ↓
Project Manager
    ↓
Architect
    ↓
Developer
    ↓
File System
    ↓
Tester
    ↓
Debugger if required
    ↓
Code Reviewer
    ↓
Documentation
    ↓
Saved Project
```

The resulting project can then be opened through **My Projects** and downloaded as a ZIP archive.

---

# Current Development Checkpoint

The following major work has been completed:

- [x] Project Manager Agent
- [x] Architect Agent
- [x] Developer Agent
- [x] File System Agent
- [x] Tester Agent
- [x] Debugger Agent
- [x] Code Reviewer Agent
- [x] Documentation Agent
- [x] LangGraph workflow
- [x] FastAPI backend
- [x] Multi-provider LLM fallback
- [x] Ollama-first provider support
- [x] Generated project files
- [x] Automated testing
- [x] Debugging loop
- [x] Code review
- [x] Documentation generation
- [x] Filesystem path protection
- [x] SQLite project persistence
- [x] Persistent project metadata
- [x] Project file viewer
- [x] Project ZIP download
- [x] Real-time agent activity streaming
- [x] Intent detection for ANSWER / CODING_HELP / BUILD_PROJECT
- [x] Frontend sidebar
- [x] DevTeam AI branding and logo
- [x] Home navigation
- [x] New Project navigation
- [x] My Projects navigation
- [x] History navigation label
- [x] Settings navigation placeholder
- [x] Frontend usability improvements
- [x] Hidden Python cache/compiled files from the project viewer
- [x] Primary/secondary button styling and focus states
- [x] Production frontend build/lint validation during the latest UI work

### Currently in progress

- [ ] Fully separate Home, My Projects and History rendering in the final App.jsx replacement
- [ ] Persistent backend conversation-history storage
- [ ] `GET /history` API
- [ ] Display persisted ANSWER/CODING_HELP conversations in History
- [ ] Ensure normal questions never create project records
- [ ] Ensure only `BUILD_PROJECT` requests enter My Projects

---

# Deployment

The current development deployment has been used with:

Backend:

```text
https://devteam-ai.onrender.com/
```

Frontend:

```text
https://devteam-ai.vercel.app/
```

For production use, persistent storage must be configured appropriately for generated projects and the SQLite database, or the persistence layer should be migrated to a managed database/storage solution.

---

# Roadmap

## Project Management

- [ ] Unique project IDs improvements
- [ ] Dedicated isolated directory for every project
- [ ] Project history enhancements
- [ ] Project status tracking
- [ ] Project deletion/management UI

## Conversation History

- [ ] Persistent conversation history
- [ ] History search
- [ ] Conversation detail view
- [ ] Delete/clear history controls
- [ ] Separate project and conversation storage

## Frontend

- [ ] More complete React dashboard
- [ ] Improved real-time agent visualization
- [ ] Generated-file editor/viewer improvements
- [ ] Project management controls
- [ ] Settings page

## Database

- [ ] PostgreSQL integration for production
- [ ] Project metadata storage in production DB
- [ ] Workflow history storage
- [ ] Conversation history storage

## Project Export

- [x] ZIP download
- [ ] Additional project export formats
- [ ] Project import

## Developer Tools

- [ ] Git integration
- [ ] GitHub integration
- [ ] Automatic repository creation
- [ ] Commit generation
- [ ] Pull request generation

## AI Infrastructure

- [ ] Provider health tracking
- [ ] Provider cooldown after quota failures
- [ ] Improved model selection
- [ ] Better agent memory
- [ ] More advanced debugging
- [ ] Better intent classification

## Security

- [ ] Stronger code-execution sandbox
- [ ] CPU and memory resource limits
- [ ] Restricted subprocess environment
- [ ] More robust generated-code isolation
- [ ] Production authentication/authorization

---

# Author

**Omm Prakash Parida**

GitHub:

https://github.com/OmmPrakash-07

Project Repository:

https://github.com/OmmPrakash-07/DevTeam-AI

---

# License

This project is currently under active development.
