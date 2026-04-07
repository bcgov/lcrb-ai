# LCRB AI Platform

AI-enabled assistant and chatbot platform for the BC Liquor and Cannabis Regulation Branch (LCRB), supporting both public-facing licensing portal users and internal BC Public Service staff.

---

## Overview

This repository contains two integrated services:

| Service | Description | Tech Stack |
|---|---|---|
| **Orchestrator** | Intent routing, RAG, application agent, feedback API | Python, FastAPI |
| **Accelerator** | Chat UI, admin panel, document ingestion pipeline | Python (Flask), React/TypeScript, Streamlit |

Both services are deployed as Azure App Services and share a common Azure AI Search index and Azure OpenAI endpoint.

---

## Repository Structure

```
lcrb-ai/
├── app.py                      # Orchestrator entry point (FastAPI)
├── requirements.txt            # Orchestrator Python dependencies
├── orchestrator/
│   ├── agents/                 # Intent-specific agents (RAG, application, screening)
│   ├── clients/                # CosmosDB feedback client
│   ├── core/                   # Session state store
│   ├── routes/                 # API routes (feedback)
│   └── schemas/                # Pydantic models
└── accelerator/
    ├── azure.yaml              # Azure Developer CLI deployment config
    ├── code/
    │   ├── app.py              # Flask backend entry point
    │   ├── frontend/           # React/TypeScript chat UI (Vite + Fluent UI)
    │   └── backend/
    │       ├── Admin.py        # Streamlit admin panel entry point
    │       ├── pages/          # Admin panel pages (Ingest, Explore, Feedback, etc.)
    │       ├── api/            # Flask API routes (chat history, feedback proxy)
    │       └── batch/          # Document processing pipeline (Azure Functions)
    └── infra/                  # Bicep infrastructure definitions
```

---

## Services & Azure Resources

| Resource | Purpose |
|---|---|
| Azure OpenAI (`gpt-4o-mini`) | Chat completions and intent routing |
| Azure OpenAI (`text-embedding-ada-002`) | Document and query embeddings |
| Azure AI Search | Vector + keyword search over ingested documents |
| Azure Blob Storage | Source document storage |
| Azure Document Intelligence | Floorplan and document validation / screening |
| Azure CosmosDB | Unified feedback storage, chat history |
| Azure Speech Service | Text-to-speech (configurable, off by default) |
| Azure App Service (`chatmvp`) | Accelerator — Flask backend + React frontend |
| Azure App Service (`lcrb-ai-orch`) | Orchestrator — FastAPI |

---

## Running Locally

### Prerequisites
- Python 3.12
- Poetry
- Node.js 24+
- `nvm` (Windows)

### 1. Orchestrator (FastAPI — port 8001)
```bash
cd lcrb-ai
pip install -r requirements.txt
uvicorn app:app --port 8001 --reload
```

### 2. Accelerator Flask backend (port 5001)
```bash
cd lcrb-ai/accelerator
python -m poetry install --no-root
python -m poetry run python -m flask --app code/app.py run --port 5001 --debug
```

### 3. React frontend (port 5173)
```bash
cd lcrb-ai/accelerator/code/frontend
nvm use 24
npm install
npm run dev
```

### 4. Streamlit admin panel (port 8501)
```bash
cd lcrb-ai/accelerator
python -m poetry run streamlit run code/backend/Admin.py --server.port 8501
```

Open **http://localhost:5173** for the chat UI and **http://localhost:8501** for the admin panel.

> **Mock mode**: Set `VITE_MOCK_MODE=true` in `accelerator/code/frontend/.env.development.local` to run the chat UI without a live backend (useful for UI development).

---

## Deploying

### Accelerator (Azure Developer CLI)
```bash
cd accelerator
azd deploy web        # Chat UI + Flask backend
azd deploy adminweb   # Streamlit admin panel
```

### Orchestrator (Azure CLI)
```bash
# From repo root — exclude accelerator/ from the zip
Get-ChildItem -Path .\lcrb-ai\ -Exclude "accelerator","__pycache__",".git",".venv","*.zip" | Compress-Archive -DestinationPath .\deploy.zip -Force

az webapp deploy \
  --resource-group "beb0bd-dev-networking" \
  --name "lcrb-ai-orch" \
  --src-path ./deploy.zip \
  --type zip --restart true
```

---

## Environment Variables

Copy `.env.example` to `.env` at the repo root (orchestrator) and `accelerator/.env` (accelerator). Key variables:

| Variable | Service | Description |
|---|---|---|
| `AZURE_OPENAI_ENDPOINT` | Both | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | Both | Azure OpenAI API key |
| `AZURE_SEARCH_SERVICE` | Both | Azure AI Search endpoint |
| `AZURE_SEARCH_KEY` | Both | Azure AI Search admin key |
| `AZURE_COSMOSDB_ACCOUNT` | Orchestrator | CosmosDB account name (feedback storage) |
| `AZURE_COSMOSDB_DATABASE` | Orchestrator | CosmosDB database name |
| `AZURE_COSMOSDB_ACCOUNT_KEY` | Orchestrator | CosmosDB primary key |
| `ORCHESTRATOR_API_URL` | Accelerator | URL of the orchestrator service |

---

## Features

### Staff Chatbot (Internal)
- RAG-based Q&A over LCRB regulatory documents, enforcement guidelines, and policy directives
- Intent routing: Q&A, navigation, application status, renewals, floorplan retrieval
- Multi-index support (Due Diligence, Licence Management, Regulations, Dynamics, Compliance & Enforcement)
- Thumbs up / thumbs down feedback with optional reason tags and free-text details

### Licensing Portal Agent (Public-facing)
- Guided Liquor Primary licence application workflow
- Document screening via Azure Document Intelligence (floorplan validation)
- Field-by-field application completion with review and fee computation
- Attachment management

### Admin Panel
- Document ingestion and re-indexing
- Data exploration and deletion
- Configuration management
- Feedback review dashboard (all sources unified via orchestrator)

---

## Architecture Notes

- The accelerator Flask backend acts as a **proxy** for feedback — it forwards submissions from the chat UI to the orchestrator's `/feedback` endpoint so all feedback lands in a single CosmosDB container regardless of source.
- The orchestrator falls back to **in-memory storage** when CosmosDB is not configured, enabling local development without Azure dependencies.
- Session state is currently **in-memory** on the orchestrator. For production, this should be migrated to a persistent store (Redis or CosmosDB).
