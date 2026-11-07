# CodeSense AI

AI-powered code review and security analysis for every pull request, with an
AI Sales Engineer that helps teams understand the platform and choose the
right plan.

CodeSense AI combines a FastAPI/LangGraph backend with a responsive React
frontend. The backend uses retrieval-augmented generation to answer product
and policy questions, enrich qualified leads, record them for sales follow-up,
and pause enterprise conversations when human review is required.

## Product capabilities

- Real-time pull request code reviews.
- Security, dependency, and secret scanning.
- Automated refactoring suggestions.
- Architecture and performance guardrails.
- GitHub, GitLab, and Bitbucket workflow support, depending on plan.
- AI-assisted plan qualification and sales conversations.
- Human-in-the-loop escalation for enterprise requirements such as on-premises
  deployment, air-gapped environments, and custom compliance needs.

## Repository structure

```text
CodeSense/
├── backend/
│   ├── api/                  FastAPI routes and Pydantic schemas
│   ├── services/             LangGraph agent, state, retrieval, and tools
│   ├── assets/               Local product documents used by retrieval
│   ├── chroma_db/            Local Chroma persistence directory
│   ├── main.py               FastAPI application entry point
│   ├── requirements.txt      Python dependencies
│   └── .env.example          Backend environment template
├── frontend/
│   ├── src/                  React application source
│   ├── package.json          Frontend scripts and dependencies
│   ├── .env.example          Frontend environment template
│   └── vite.config.ts        Vite configuration
├── docs/
│   ├── HANDOFF.md            Product and backend/frontend handoff
│   ├── FRONTEND_README.md    Frontend-specific documentation
│   └── CODESENSE_UI_COPILOT_PROMPT.md
├── .gitignore
└── README.md
```

Local credentials, vector databases, dependency folders, build output, and
Python cache files are intentionally excluded from Git by
[.gitignore](./.gitignore).

## Technology stack

### Backend

- Python 3.11
- FastAPI and Uvicorn
- LangGraph and LangChain
- Groq-hosted chat model
- Chroma vector store
- Hugging Face embeddings
- BM25 and dense retrieval
- Pydantic request and response schemas

### Frontend

- React 18
- TypeScript with strict checking
- Vite
- React Router
- Tailwind CSS
- Lucide React icons
- Fraunces, Inter, and JetBrains Mono fonts

## Requirements

Install the following before starting:

- Python 3.11
- Node.js 18 or newer
- npm
- Git

Python 3.11 is recommended for the backend because some LangChain and Chroma
dependencies may not support every newer Python version.

## Configuration

### Backend environment

Create `backend/.env` from the template:

```powershell
Copy-Item backend\.env.example backend\.env
```

Set the required credentials:

```env
ABSTRACT_API_KEY=your_company_enrichment_key
GROQ_API_KEY=your_groq_api_key
```

Never commit `backend/.env` or place credentials in frontend code.

### Frontend environment

Create `frontend/.env` from the template:

```powershell
Copy-Item frontend\.env.example frontend\.env
```

The default configuration is:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Only the public API base URL belongs in the frontend environment. API keys
must remain on the backend.

When deploying the frontend to Vercel, set `VITE_API_BASE_URL` in the Vercel
project environment variables to the public backend URL, for example:

```env
VITE_API_BASE_URL=https://your-backend.onrender.com/api/v1
```

The Vercel configuration in `frontend/vercel.json` preserves React Router
routes such as `/pricing`, `/security`, and `/chat` on direct navigation.

## Run locally

Run the backend and frontend in separate terminals.

### 1. Start the backend

Using Conda:

```powershell
cd E:\AdvancedProjects\CodeSense\backend
conda activate langchain
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Alternatively, use a Python 3.11 executable directly:

```powershell
cd E:\AdvancedProjects\CodeSense\backend
& "C:\Path\To\Python311\python.exe" -m pip install -r requirements.txt
& "C:\Path\To\Python311\python.exe" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:

- Health check: <http://localhost:8000/>
- Swagger API documentation: <http://localhost:8000/docs>
- ReDoc API documentation: <http://localhost:8000/redoc>

### 2. Start the frontend

```powershell
cd E:\AdvancedProjects\CodeSense\frontend
npm install
npm run dev
```

Open the URL printed by Vite, normally:

<http://localhost:5173/>

## Frontend commands

Run these from `frontend/`:

```powershell
npm run dev       # Start the Vite development server
npm run build     # Type-check and create a production build
npm run preview   # Preview the production build locally
```

The production build runs strict TypeScript validation before Vite bundles the
application.

## API overview

The API is mounted under `/api/v1`.

### Send a chat message

```http
POST /api/v1/chat
Content-Type: application/json
```

Request:

```json
{
  "thread_id": "session-108",
  "message": "Which plan is best for a 10-person engineering team?"
}
```

Completed response:

```json
{
  "thread_id": "session-108",
  "status": "COMPLETED",
  "response": "The Team plan is the best fit ...",
  "interrupt_details": null
}
```

Interrupted response:

```json
{
  "thread_id": "session-108",
  "status": "INTERRUPTED",
  "response": "Your request requires enterprise review...",
  "interrupt_details": {
    "status": "Action Required",
    "message": "Custom compliance or On-Premise deployment requested.",
    "instructions": "Accept the enterprise decision or override it."
  }
}
```

Additional endpoints:

```text
GET  /api/v1/pending_reviews/{thread_id}
POST /api/v1/approve_escalation
```

The approval endpoint is intended for a future authenticated internal sales
workflow and is not exposed in the public visitor UI.

## Conversation behavior

The frontend:

- Generates a thread ID automatically.
- Stores the active thread ID in `sessionStorage`.
- Reuses the same thread ID for the current browser session.
- Supports a new-conversation action.
- Handles completed, interrupted, loading, timeout, network, and server-error
  states.
- Keeps enterprise escalation visible as a human-review state rather than
  presenting it as a generic failure.

The backend currently uses an in-memory LangGraph checkpointer. Active
conversation state is therefore not durable across backend restarts.

## Retrieval data

Product and commercial policy content is stored locally under
`backend/assets/`. The backend uses this content to answer questions about
pricing, integrations, policies, and enterprise capabilities.

The Chroma persistence directory is local runtime data and is ignored by Git.
For a fresh environment, the retrieval layer may need to create or rebuild
its local index.

## Security notes

- Do not commit `.env` files, API keys, tokens, or local CRM data.
- Do not expose backend credentials through Vite environment variables.
- Restrict FastAPI CORS origins before production deployment.
- The current development CORS configuration allows all origins and should be
  replaced with the deployed frontend origin in production.
- Avoid sending secrets, credentials, or private source code into the public
  sales chat.
- Review dependency audit warnings before a production deployment.

## Documentation

- [Product and implementation handoff](./docs/HANDOFF.md)
- [Frontend setup and API notes](./docs/FRONTEND_README.md)
- [UI build prompt](./docs/CODESENSE_UI_COPILOT_PROMPT.md)
- [Backend requirements](./backend/requirements.txt)

## Current status

The local development experience includes:

- A working FastAPI backend with chat and escalation routes.
- A responsive React marketing site.
- Pricing, platform, security, and workflow content.
- A shared AI Sales Engineer chat experience.
- Typed frontend API integration.
- Strict TypeScript and Vite production builds.

Before deploying publicly, add authentication for internal escalation approval,
restrict CORS, configure production persistence, and review all dependency and
operational security settings.
