# SupportFlow RAG Portfolio

SupportFlow RAG is a portfolio implementation of an internal knowledge RAG system for a fictional B2B inquiry-management SaaS operated by Northstar Systems.

It demonstrates document ingestion, hybrid retrieval, grounded answer generation, source display, abstention, evaluation, Docker-based local operation, and AWS-oriented operations design.

## What This Shows

- Python/FastAPI backend for RAG APIs
- React/Vite frontend with Ask, Documents, Evaluation, and Logs tabs
- Built-in sample documents for a fictional inquiry-management SaaS
- Markdown, TXT, CSV, JSON, PDF, and DOCX ingestion strategy
- Hybrid retrieval with keyword and vector-ready scoring
- OpenRouter and local LLM provider abstraction
- SQLite logs and metadata
- RAG evaluation with Recall@k, MRR, citation rate, abstention accuracy, and keyword matching
- Docker Compose local demo without a permanently hosted API
- Documentation for AWS ECS/Fargate-style production operation

## Deployment Policy

The live RAG API is intentionally not hosted permanently. This avoids maintenance cost and API billing risk.

Live presentation:

- https://supportflow-rag-portfolio.pages.dev

Recommended portfolio flow:

- Cloudflare Pages hosts the one-page HTML explanation in `presentation/`.
- The real RAG app runs locally with Docker Compose during a screen-share demo.
- For a no-API-key local LLM demo on low-memory laptops, run the native Ollama mode instead of Docker Compose.
- Reviewers can clone the GitHub repository and run the same local demo.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Open:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

The default `.env.example` uses `LLM_PROVIDER=mock` so the app can start without an API key. For a real model, set either OpenRouter or Ollama.

If those ports are already in use, change `BACKEND_PORT`, `FRONTEND_PORT`, and `VITE_API_BASE_URL` in `.env` before rebuilding. Example: `BACKEND_PORT=8011`, `FRONTEND_PORT=5179`, `VITE_API_BASE_URL=http://localhost:8011/api`.

## LLM Modes

### OpenRouter

Set:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=selected_model_later
```

The concrete model is intentionally not fixed in this repository plan.

### Ollama

Run Ollama locally, pull a model of your choice, then set:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=selected_local_model_later
```

For the current low-memory Windows demo machine, the verified Google local model is:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:1b
```

Gemma 4 and Gemma 3 4B-class models are better quality choices on stronger hardware, but they were not reliable on an 8GB RAM laptop while the RAG stack was running. The repository therefore keeps the provider configurable instead of hard-coding one model.

Native Ollama demo on Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_native_ollama_demo.ps1
```

Open `http://localhost:5179`. Stop it with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop_native_demo.ps1
```

### Mock

`LLM_PROVIDER=mock` is only for local fallback and automated tests. It is not presented as the production-quality model path.

## Repository Layout

```text
backend/       FastAPI backend, RAG pipeline, SQLite, tests
frontend/      React/Vite web UI
sample_docs/   Built-in fictional SupportFlow documents
evaluation/    QA dataset and expected sources
docs/          Design, AWS architecture, operations, evaluation report
presentation/  Screen-share HTML explanation for Cloudflare Pages
```

## Test Commands

Docker smoke test:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\docker_smoke_test.ps1
```

If the images are already built and containers are already running:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\docker_smoke_test.ps1 -SkipBuild
```

The smoke test checks Docker Compose config, starts the app, waits for backend health, verifies the frontend, calls the Ask API, and runs the evaluation dataset.

Backend:

```bash
cd backend
python -m pytest
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env
npm run build
```

## Notes

- This is a portfolio project, not a production SaaS.
- Authentication is represented by demo roles only. Production authentication is documented as Cognito or internal SSO.
- Cloudflare Pages is used for static explanation material, not for hosting the Python RAG API.
