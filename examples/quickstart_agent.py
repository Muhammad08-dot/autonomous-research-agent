"""
Quickstart for the Self-Improving Autonomous Research Agent.

Demonstrates two ways to interact with the system:
  1. Direct LangGraph invocation - runs the research crew in-process (no server needed).
  2. FastAPI client - calls the running HTTP API (/health and /generate).

Usage:
    # Direct graph invocation only:
    python examples/quickstart_agent.py

    # With the API server running (default http://localhost:8006):
    python app.py            # terminal 1 - start the server
    python examples/quickstart_agent.py
"""
from __future__ import annotations

import os
import sys

import httpx

BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
sys.path.insert(0, BACKEND_DIR)

from app.agents.research_crew_agent import research_agent_graph  # noqa: E402

API_BASE_URL = os.environ.get("RESEARCH_API_BASE_URL", "http://localhost:8006")
TOPIC = "Autonomous AI Agents"


def empty_state(topic: str) -> dict:
    """A research state matching the LangGraph ResearchState schema."""
    return {
        "topic": topic,
        "plan_outline": [],
        "scraped_facts": [],
        "verified_sources": [],
        "draft_report": "",
        "reflection_notes": "",
        "final_report": "",
    }


def invoke_graph_directly(topic: str) -> dict:
    """Run the full Planner -> Scraper -> Fact-Checker -> Writer -> Reviewer pipeline."""
    print(f"\n=== 1. Direct LangGraph invocation (topic: {topic!r}) ===")
    result = research_agent_graph.invoke(empty_state(topic))

    print("Outline:")
    for section in result["plan_outline"]:
        print(f"  - {section}")

    print("Verified sources:")
    for source in result["verified_sources"]:
        print(f"  - {source}")

    print("Final report:")
    print(result["final_report"])
    return result


def call_api(topic: str) -> None:
    """Exercise the FastAPI server over HTTP using an httpx client."""
    print(f"\n=== 2. FastAPI client (base URL: {API_BASE_URL}) ===")
    try:
        with httpx.Client(base_url=API_BASE_URL, timeout=30.0) as client:
            health = client.get("/health")
            health.raise_for_status()
            print(f"GET /health -> {health.status_code} {health.json()}")

            response = client.post(
                "/api/v1/research/generate",
                json={"topic": topic},
            )
            response.raise_for_status()
            payload = response.json()

            print(f"POST /api/v1/research/generate -> {response.status_code}")
            print(f"  topic : {payload['topic']}")
            print(f"  outline: {len(payload['outline'])} sections")
            print(f"  report: {payload['final_report']!r:.80}...")
    except httpx.HTTPError as exc:
        print(f"Could not reach the API at {API_BASE_URL} ({exc}).")
        print("Start the server first, e.g.: python app.py")
        print("Skipping the FastAPI client section.")


def main() -> None:
    invoke_graph_directly(TOPIC)
    call_api(TOPIC)


if __name__ == "__main__":
    main()