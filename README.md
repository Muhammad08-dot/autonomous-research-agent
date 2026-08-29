# 🤖 Self-Improving Autonomous Research Agent

Production-Grade Agentic Workflow Platform with Multi-Agent Collaboration (Planner → Web Scraper → Fact-Checker → Writer → Reviewer), Self-Reflection Loops, Long-Term Memory, and Automated Report Synthesis.

The agent pipeline is a [LangGraph](https://www.langchain.com/langgraph) state machine. A request flows through five agent nodes:

```
Planner ──▶ Scraper ──▶ Fact-Checker ──▶ Writer ──▶ Reviewer ──▶ Final Report
```

## Architecture

- **Backend:** FastAPI (Python 3.11+) + LangGraph Multi-Agent Orchestration + Prometheus metrics
- **Agents:** `backend/app/agents/research_crew_agent.py`
- **API:** `backend/app/api/v1/endpoints/research.py`
- **Frontend:** Next.js 15 + TypeScript + TailwindCSS
- **Infrastructure:** Docker Compose (`infrastructure/docker/docker-compose.dev.yml`)

## Repository Structure

```
├── app.py                         # Root runnable entrypoint (adds backend/ to path)
├── main.py                        # uvicorn entrypoint (backend.app.main:app)
├── streamlit_app.py               # Streamlit dashboard
├── backend/
│   └── app/
│       ├── main.py                # FastAPI app factory + /health
│       ├── agents/
│       │   └── research_crew_agent.py   # LangGraph agent nodes + graph
│       ├── api/v1/endpoints/
│       │   └── research.py        # POST /api/v1/research/generate
│       └── core/
│           └── config.py          # Pydantic v2 settings (.env)
├── examples/
│   └── quickstart_agent.py        # Runnable usage examples
├── tests/                         # pytest unit tests
└── .env.example                   # Environment variable template
```

## Prerequisites

- Python 3.11+
- pip / venv
- Optional: Docker + Docker Compose for infrastructure (PostgreSQL, Redis, Qdrant)

## Installation

```bash
# 1. Clone the repository
git clone <repo-url> autonomous-research-agent
cd autonomous-research-agent

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# ...edit .env to match your environment...
```

## Environment Variables

Copy `.env.example` to `.env` and adjust values. All variables are optional — sensible defaults are provided in `backend/app/core/config.py`.

| Variable                  | Default                                                                                                | Description                                  |
| ------------------------- | ------------------------------------------------------------------------------------------------------ | -------------------------------------------- |
| `PROJECT_NAME`            | `Self-Improving Autonomous Research Agent`                                                             | Service name shown in API docs and /health   |
| `API_V1_STR`              | `/api/v1`                                                                                              | URL prefix for versioned API routes          |
| `ENVIRONMENT`             | `development`                                                                                          | Runtime environment label                    |
| `SECRET_KEY`              | `research_agent_secret_key_33221100`                                                                   | Secret for signing/session material          |
| `BACKEND_CORS_ORIGINS`    | `["http://localhost:3000", "http://localhost:3006", "http://localhost:8006"]`                          | JSON-encoded list of allowed CORS origins    |
| `DATABASE_URL`            | `postgresql+asyncpg://research_user:research_secret_44@localhost:5438/research_agent_db`               | Async SQLAlchemy database URL                |
| `REDIS_URL`               | `redis://localhost:6385/0`                                                                             | Redis connection URL                         |
| `QDRANT_URL`              | `http://localhost:6338`                                                                                | Qdrant vector store base URL                 |

Note: list-valued settings (e.g. `BACKEND_CORS_ORIGINS`) must be JSON-encoded in the `.env` file.

## Running the API Server

```bash
# Option A — runnable entrypoint (adds backend/ to sys.path automatically)
python app.py

# Option B — uvicorn directly
uvicorn backend.app.main:app --host 0.0.0.0 --port 8006 --reload

# Option C — Docker Compose (infrastructure + backend)
docker compose -f infrastructure/docker/docker-compose.dev.yml up --build
```

Once running, open:

- Interactive API docs: <http://localhost:8006/docs>
- OpenAPI schema: <http://localhost:8006/api/v1/openapi.json>
- Metrics: <http://localhost:8006/metrics>

## API Endpoints

### 1. Health Check

**`GET /health`** — liveness probe.

**Example:**

```bash
curl http://localhost:8006/health
```

**Response `200 OK`:**

```json
{
  "status": "healthy",
  "service": "Self-Improving Autonomous Research Agent"
}
```

| Field     | Type   | Description                     |
| --------- | ------ | ------------------------------- |
| `status`  | string | Always `"healthy"` when up      |
| `service` | string | Value of `PROJECT_NAME` setting |

### 2. Generate Research Report

**`POST /api/v1/research/generate`** — runs the full LangGraph research crew and returns the synthesized report.

**Request body (`application/json`):**

| Field   | Type   | Required | Description                         |
| ------- | ------ | -------- | ----------------------------------- |
| `topic` | string | yes      | Research topic to investigate        |

**Example:**

```bash
curl -X POST http://localhost:8006/api/v1/research/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Large Language Models"}'
```

**Response `200 OK`:**

```json
{
  "topic": "Large Language Models",
  "outline": [
    "1. Executive Summary of Large Language Models",
    "2. Historical Context & Technical Architecture",
    "3. Market Impact & Future Projections"
  ],
  "sources": [
    "https://arxiv.org/abs/2401.99821 (Verified IEEE Peer Review)",
    "https://nature.com/articles/s41586-024 (Verified Primary Source)"
  ],
  "final_report": "# Comprehensive Technical Report: Large Language Models\n\n## 1. Executive Summary\n..."
}
```

**Error responses:**

| Status | When                                                          |
| ------ | ------------------------------------------------------------- |
| `422`  | Request body is missing, `topic` is absent, or not a string   |

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "topic"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

## Running the Example Script

See [examples/quickstart_agent.py](examples/quickstart_agent.py) for a runnable walkthrough of both invocation styles:

```bash
# Direct LangGraph invocation (no server required)
python examples/quickstart_agent.py

# With the API server running on :8006, the same script also calls /health and /generate
```

## Running Tests

```bash
python -m pytest
```

## License

MIT