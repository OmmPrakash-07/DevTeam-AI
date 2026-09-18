# DevTeam AI 🤖

> **Multi-Agent Autonomous Software Development Team**

DevTeam AI is an AI-powered software development system designed to take a software idea and process it through multiple specialized development agents.

The long-term goal is to automate a complete software development workflow:

**Requirements → Architecture → Development → Testing → Debugging → Code Review → Documentation**

---

## 🚀 Current Progress

The project is currently in the early backend/workflow development stage.

### Implemented

- ✅ FastAPI backend
- ✅ Gemini API integration
- ✅ LangGraph workflow
- ✅ Shared project state
- ✅ Project Manager Agent
- ✅ Architect Agent
- ✅ Developer Agent
- ✅ Project Manager → Architect → Developer workflow
- ✅ `/generate` API endpoint
- ✅ JSON-based architecture generation
- ✅ Developer agent source-file planning
- ✅ Environment variable support using `.env`

### Current Workflow

```text
User Request
     │
     ▼
Project Manager Agent
     │
     ▼
Architect Agent
     │
     ▼
Developer Agent
     │
     ▼
Generated Project Files
```

---

## 🧠 Agents

### 1. Project Manager Agent

Analyzes the user's software idea and extracts the main software requirements.

**Input:**
- User's software request

**Output:**
- List of software requirements

---

### 2. Architect Agent

Converts the requirements into a technical architecture.

It currently generates information such as:

- Project type
- Frontend technology
- Backend technology
- Database
- Authentication
- API style
- Folder structure

**Output:**
- Structured architecture in JSON format

---

### 3. Developer Agent

Uses the requirements and architecture to design the initial project source files.

It generates:

- File paths
- Source code
- Initial project files

**Output:**
- Generated file list
- File contents stored in the workflow state

> File writing to the final generated project directory is part of the upcoming development stages.

---

## 🛠️ Tech Stack

### Backend

- Python
- FastAPI
- LangGraph
- LangChain
- Google Gemini API
- python-dotenv

### Frontend

The planned frontend stack is:

- React
- Vite
- Tailwind CSS

Frontend implementation is planned for a later stage.

### Planned Technologies

- PostgreSQL
- Chroma / FAISS
- Sandboxed code execution
- Git / GitHub integration

---

## 📁 Project Structure

```text
devteam-ai/
│
├── backend/
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── project_manager.py
│   │   ├── architect.py
│   │   └── developer.py
│   │
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   └── workflow.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── llm.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   └── filesystem.py
│   │
│   ├── main.py
│   └── .env
│
├── frontend/
│
├── generated_projects/
│
└── tests/
```

> `backend/.env` is a local configuration file and should **not** be committed to GitHub.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/OmmPrakash-07/DevTeam-AI.git
```

Then:

```bash
cd DevTeam-AI
```

---

### 2. Open the backend

```powershell
cd backend
```

---

### 3. Create a Python virtual environment

Windows PowerShell:

```powershell
python -m venv venv
```

Activate it:

```powershell
.env\Scripts\Activate.ps1
```

---

### 4. Install dependencies

```powershell
pip install -U langchain-google-genai
pip install -U langgraph langchain python-dotenv fastapi uvicorn
```

---

## 🔑 Environment Variables

Create:

```text
backend/.env
```

Add:

```env
GEMINI_API_KEY=your_api_key_here
```

Do **not** add your real API key to GitHub.

The project uses `python-dotenv` to load the key from the `.env` file.

---

## ▶️ Running the Backend

From the `backend` directory:

```powershell
uvicorn main:app --reload
```

The backend should start at:

```text
http://127.0.0.1:8000
```

---

## 🧪 API

### Health Check

Open:

```text
GET /
```

Expected response:

```json
{
  "message": "DevTeam AI is running 🚀"
}
```

---

### Generate Project

Endpoint:

```text
POST /generate
```

Example request:

```json
{
  "request": "Build a bike rental web application"
}
```

The workflow processes the request through:

```text
Project Manager
       ↓
    Architect
       ↓
    Developer
```

The response currently contains:

- User request
- Requirements
- Architecture
- Generated file names
- Generated file information

---

## 🔄 LangGraph Workflow

The current workflow is implemented using LangGraph.

```text
START
  │
  ▼
Project Manager
  │
  ▼
Architect
  │
  ▼
Developer
  │
  ▼
END
```

The workflow uses a shared `ProjectState` object to pass information between agents.

---

## 📦 Project State

The shared state currently supports:

```text
user_request
requirements
architecture
tasks
generated_files
test_results
errors
review
final_response
```

This state is designed to support the future multi-agent workflow.

---

## 🗺️ Roadmap

### Phase 1 — Core Workflow

- [x] Project Manager Agent
- [x] Architect Agent
- [x] Developer Agent
- [x] LangGraph workflow
- [x] Gemini integration

### Phase 2 — Project Generation

- [ ] File System Agent
- [ ] Create generated project directories
- [ ] Write generated source files
- [ ] Project templates
- [ ] Better code-generation validation

### Phase 3 — Testing

- [ ] Tester Agent
- [ ] Automated test execution
- [ ] Error collection
- [ ] Test result reporting

### Phase 4 — Debugging

- [ ] Debugger Agent
- [ ] Automatic error analysis
- [ ] Automatic code fixes
- [ ] Re-test after fixes

### Phase 5 — Code Quality

- [ ] Code Reviewer Agent
- [ ] Security checks
- [ ] Code quality analysis
- [ ] Architecture validation

### Phase 6 — Documentation

- [ ] Documentation Agent
- [ ] Automatic README generation
- [ ] API documentation
- [ ] Project documentation

### Phase 7 — Multi-Provider LLM

Planned support for multiple LLM providers:

```text
Gemini
  │
  ├── Groq
  │
  └── OpenRouter
```

The goal is to make the LLM layer provider-independent and allow controlled fallback between supported providers.

### Phase 8 — Frontend

- [ ] React frontend
- [ ] Vite setup
- [ ] Tailwind CSS
- [ ] Project-generation dashboard
- [ ] Agent execution status
- [ ] Generated code viewer
- [ ] Test results dashboard

---

## 🔐 Security

Never commit secrets to GitHub.

The following files should remain local:

```text
.env
venv/
__pycache__/
```

Recommended `.gitignore` entries:

```gitignore
backend/.env
backend/venv/
__pycache__/
*.pyc
.env
node_modules/
dist/
```

If an API key is accidentally exposed, revoke it and create a new one.

---

## 📌 Current Limitations

The project is still under active development.

Currently:

- The workflow generates requirements and architecture using an LLM.
- The Developer Agent generates source-file information but the complete automated project-writing pipeline is not finished.
- Testing and debugging agents are not implemented yet.
- The React frontend is not implemented yet.
- Database integration is planned.
- LLM provider fallback is planned.

---

## 📈 Development Workflow

For each major feature:

```text
1. Implement
      ↓
2. Test
      ↓
3. Update README
      ↓
4. Git add
      ↓
5. Git commit
      ↓
6. Git push
```

Example:

```powershell
git add .
git commit -m "Add Tester Agent"
git push origin main
```

The README should be updated whenever a significant feature, agent, architecture change, setup requirement, or API change is introduced.

---

## 👨‍💻 Project

**DevTeam AI**

GitHub:

https://github.com/OmmPrakash-07/DevTeam-AI

---

## 📄 License

License information will be added as the project progresses.

---

### ⭐ Project Status

**Status: 🚧 Active Development**

Current milestone:

```text
Project Manager → Architect → Developer
```

Next major milestone:

```text
Developer → File System → Tester → Debugger
```
