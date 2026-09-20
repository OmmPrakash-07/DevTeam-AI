# DevTeam AI

> **Multi-Agent Autonomous Software Development Team**

DevTeam AI is an AI-powered software development system that uses multiple specialized agents to automate the software development workflow.

Instead of relying on a single AI agent, DevTeam AI divides the development process into specialized roles such as requirements analysis, architecture design, coding, file generation, testing, debugging, code review, and documentation.

---

## Overview

DevTeam AI follows an automated development pipeline:

```text
User Request
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
File System Agent
     |
     v
Tester
     |
     +---- Tests Failed ----> Debugger
     |                         |
     |                         v
     |                       Tester
     |
     +---- Tests Passed -----> Code Reviewer
                                  |
                                  v
                            Documentation
                                  |
                                  v
                                 END
```

The workflow is orchestrated using **LangGraph**, while the backend API is built with **FastAPI**.

---

## Features

- Multi-agent software development workflow
- Automated requirement analysis
- AI-generated project architecture
- Automated source-code generation
- Automatic project file creation
- Automated testing
- Debugging loop for failed tests
- AI-based code review
- Automatic documentation generation
- Multiple LLM provider fallback
- Path traversal protection for generated files
- Python AST validation
- Test execution with timeouts
- REST API for project generation

---

## AI Agents

DevTeam AI currently contains **8 specialized agents**.

| Agent             | Responsibility                                                               |
| ----------------- | ---------------------------------------------------------------------------- |
| Project Manager   | Converts the user request into structured requirements and development tasks |
| Architect         | Designs the project architecture and folder structure                        |
| Developer         | Generates source code, tests, and project documentation                      |
| File System Agent | Creates the generated project files safely                                   |
| Tester            | Validates and executes generated tests                                       |
| Debugger          | Fixes errors detected during testing                                         |
| Code Reviewer     | Reviews the generated implementation for quality and issues                  |
| Documentation     | Generates project documentation based on the actual project                  |

---

## Workflow Logic

The current workflow is implemented using LangGraph.

### 1. Project Manager

Receives the user's software request and determines the requirements and tasks.

### 2. Architect

Creates an architecture based on the actual project requirement.

The architecture is not restricted to web applications. Depending on the request, it can describe projects such as:

- Python CLI applications
- Automation tools
- Backend/API applications
- Desktop applications
- Full-stack applications
- Other software systems

### 3. Developer

Generates the required project files according to the architecture and requirements.

The developer is instructed to avoid unnecessarily inventing:

- Frameworks
- Databases
- APIs
- Authentication systems
- Dependencies
- Modules
- Classes
- Services

### 4. File System Agent

Writes the generated files into the project's generated-project directory.

The file system layer also prevents:

- Absolute paths
- Path traversal
- Writing files outside the generated project directory

### 5. Tester

The tester performs validation and testing.

For Python projects it can:

- Validate Python syntax using AST
- Detect problematic imports
- Execute unit tests
- Execute suitable non-interactive Python modules
- Detect test failures
- Apply execution timeouts

The current default Python test command is:

```bash
python -m unittest discover -s tests
```

### 6. Debugger

If tests fail, the debugger receives the relevant project information and attempts to fix the generated files.

The workflow can repeat the:

```text
Tester -> Debugger -> Tester
```

cycle.

The current workflow allows up to **3 debugging attempts** before continuing to code review.

### 7. Code Reviewer

After testing succeeds, the generated project is reviewed for:

- Code quality
- Potential issues
- Maintainability
- Implementation consistency
- Unnecessary complexity

### 8. Documentation Agent

Finally, documentation is generated based on the project and its implementation.

---

## Technology Stack

### Backend

- Python
- FastAPI
- LangGraph
- LangChain
- python-dotenv

### AI / LLM Providers

DevTeam AI currently supports a fallback sequence involving:

1. Google Gemini
2. Groq
3. DeepSeek
4. Anthropic Claude
5. OpenRouter

The system attempts the configured providers in sequence when an earlier provider fails.

### Project Execution

- Python subprocess execution
- Python AST validation
- `unittest`
- File-system safety validation

---

## Project Structure

```text
devteam-ai/
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
|   |
|   +-- tools/
|   |   +-- __init__.py
|   |   +-- filesystem.py
|   |
|   +-- main.py
|   +-- .env
|
+-- frontend/
|
+-- generated_projects/
|
+-- tests/
|
+-- .gitignore
+-- README.md
```

---

## Requirements

Make sure the following are installed:

- Python 3.10+
- pip
- Git

Recommended Python packages:

```bash
pip install -U langchain-google-genai
pip install -U langgraph langchain python-dotenv fastapi uvicorn
pip install -U anthropic openai
```

---

## Configuration

Create a `.env` file inside the `backend` directory.

```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

Only configure the providers you intend to use.

### Security

Do not commit API keys to GitHub.

The repository `.gitignore` excludes:

```text
backend/.env
.env
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/OmmPrakash-07/DevTeam-AI.git
```

Move into the project:

```bash
cd DevTeam-AI
```

Create a virtual environment:

```bash
python -m venv backend/venv
```

Activate it on Windows:

```powershell
backend\venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -U langchain-google-genai langgraph langchain python-dotenv fastapi uvicorn anthropic openai
```

---

## Running the Backend

Move into the backend directory:

```powershell
cd backend
```

Start FastAPI:

```powershell
uvicorn main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## API

### Health Check

```http
GET /
```

Example response:

```json
{
  "message": "DevTeam AI is running"
}
```

---

### Generate Project

```http
POST /generate
```

Request:

```json
{
  "request": "Create a simple Python calculator application"
}
```

Example PowerShell request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/generate" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"request":"Create a simple Python calculator application"}'
```

The response contains information such as:

- User request
- Requirements
- Architecture
- Generated files
- Tasks
- Test results
- Code review
- Debug attempts

---

## Generated Projects

Generated applications are currently stored inside:

```text
generated_projects/
```

For example:

```text
generated_projects/
└── generated_project/
    ├── src/
    ├── tests/
    └── README.md
```

The current implementation uses a generated project directory for the workflow.

> **Note:** Unique project IDs and isolated project directories are planned for a future version.

---

## Testing DevTeam AI

A simple end-to-end test can be performed by sending a project-generation request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/generate" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"request":"Create a simple Python calculator application"}'
```

A successful workflow should proceed through:

```text
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
Code Reviewer
    ↓
Documentation
```

If generated tests fail, the workflow can enter:

```text
Tester
   ↓
Debugger
   ↓
Tester
```

until the tests pass or the debugging-attempt limit is reached.

---

## Error Handling

The system includes several layers of validation.

### API Validation

An empty project request is rejected.

### File System Validation

The file system tool prevents:

```text
Absolute paths
Path traversal
Writing outside the project directory
```

### Code Validation

Python source files can be parsed using Python's AST parser before execution.

### Test Validation

The tester checks generated tests and executes appropriate test suites.

### LLM Fallback

If one configured LLM provider fails, the router can attempt another configured provider.

---

## Current Status

### Implemented

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
- [x] Generated project files
- [x] Automated testing
- [x] Debugging loop
- [x] Code review
- [x] Documentation generation
- [x] File-system path protection

---

## Roadmap

The following features are planned for future development:

### Project Management

- [ ] Unique project IDs
- [ ] Separate folder for every generated project
- [ ] Project history
- [ ] Project status tracking

### Frontend

- [ ] React dashboard
- [ ] Tailwind CSS interface
- [ ] Real-time agent activity
- [ ] Project generation interface
- [ ] Generated-file viewer
- [ ] Test-result dashboard

### Database

- [ ] PostgreSQL integration
- [ ] Store project metadata
- [ ] Store workflow history
- [ ] Store generated project information

### Project Export

- [ ] ZIP download
- [ ] Project export
- [ ] Generated-project management

### Developer Tools

- [ ] Git integration
- [ ] GitHub integration
- [ ] Automatic repository creation
- [ ] Commit generation

### AI Infrastructure

- [ ] Provider health tracking
- [ ] Provider cooldown after quota failures
- [ ] Improved model selection
- [ ] Better agent memory
- [ ] More advanced debugging

### Security

- [ ] Stronger code-execution sandbox
- [ ] Resource limits
- [ ] Restricted subprocess environment
- [ ] More robust generated-code isolation

---

## Project Vision

The long-term goal of DevTeam AI is to create an autonomous software engineering environment where a user can provide a software idea and an AI development team can collaboratively transform that idea into a working software project.

The system is designed around the concept of specialized AI agents working together rather than a single general-purpose coding agent.

```text
Idea
 ↓
Requirements
 ↓
Architecture
 ↓
Implementation
 ↓
Files
 ↓
Testing
 ↓
Debugging
 ↓
Code Review
 ↓
Documentation
 ↓
Software Project
```

---

## Author

**Omm Prakash Parida**

GitHub:

```text
https://github.com/OmmPrakash-07
```

Project Repository:

```text
https://github.com/OmmPrakash-07/DevTeam-AI
```

---

## License

This project is currently under development.
