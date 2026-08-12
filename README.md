# 🤖 Self-Improving Autonomous Research Agent Team

Production-Grade Agentic Workflow Platform with Multi-Agent Collaboration (Planner, Web Scraper, Fact-Checker, Writer, Reviewer), Self-Reflection Loops, Long-Term Memory, and Automated PDF/LaTeX Report Synthesis.

## Architecture

- **Backend:** FastAPI (Python 3.11+) + LangGraph + CrewAI Hybrid Agent Orchestration + Qdrant Vector Store
- **Memory:** Long-Term Experience Replay & Reflection Store
- **Frontend:** Next.js 15 + TypeScript + TailwindCSS
- **Infrastructure:** Docker Compose

## Quick Start

```bash
cd autonomous_research_agent
docker compose -f infrastructure/docker/docker-compose.dev.yml up --build
```
