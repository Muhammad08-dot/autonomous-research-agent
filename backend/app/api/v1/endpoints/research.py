"""
Autonomous Research Generation API Endpoints
"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.research_crew_agent import research_agent_graph

router = APIRouter()


class ResearchRequest(BaseModel):
    topic: str


@router.post("/generate")
async def generate_research_report(payload: ResearchRequest):
    initial_state = {
        "topic": payload.topic,
        "plan_outline": [],
        "scraped_facts": [],
        "verified_sources": [],
        "draft_report": "",
        "reflection_notes": "",
        "final_report": ""
    }

    result = research_agent_graph.invoke(initial_state)

    return {
        "topic": payload.topic,
        "outline": result["plan_outline"],
        "sources": result["verified_sources"],
        "final_report": result["final_report"]
    }
