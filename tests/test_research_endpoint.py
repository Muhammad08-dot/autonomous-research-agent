import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.v1.endpoints.research import ResearchRequest
from app.main import app

client = TestClient(app)

GENERATE_URL = "/api/v1/research/generate"


class TestResearchRequestModel:
    def test_valid_topic(self):
        request = ResearchRequest(topic="Autonomous Agents")
        assert request.topic == "Autonomous Agents"

    def test_empty_topic_allowed(self):
        assert ResearchRequest(topic="").topic == ""

    def test_missing_topic_rejected(self):
        with pytest.raises(ValidationError):
            ResearchRequest()

    def test_none_topic_rejected(self):
        with pytest.raises(ValidationError):
            ResearchRequest(topic=None)

    def test_non_string_topic_rejected(self):
        with pytest.raises(ValidationError):
            ResearchRequest(topic=123)

    def test_extra_fields_ignored(self):
        request = ResearchRequest(topic="AI", unsupported="ignored")
        assert request.topic == "AI"


class TestGenerateResearchEndpoint:
    def test_generate_returns_200_with_full_contract(self):
        response = client.post(GENERATE_URL, json={"topic": "Quantum AI"})
        assert response.status_code == 200
        payload = response.json()
        assert set(payload.keys()) == {"topic", "outline", "sources", "final_report"}

    def test_generate_outline_embeds_topic(self):
        response = client.post(GENERATE_URL, json={"topic": "Edge Computing"})
        payload = response.json()
        assert payload["topic"] == "Edge Computing"
        assert len(payload["outline"]) == 3
        assert payload["outline"][0] == "1. Executive Summary of Edge Computing"

    def test_generate_sources_are_verified(self):
        response = client.post(GENERATE_URL, json={"topic": "AI"})
        payload = response.json()
        assert len(payload["sources"]) == 2
        assert all(source.startswith("https://") for source in payload["sources"])

    def test_generate_final_report_end_to_end(self):
        response = client.post(GENERATE_URL, json={"topic": "LLMs"})
        payload = response.json()
        assert payload["final_report"].startswith("# Comprehensive Technical Report: LLMs")
        assert "Self-Reflection Score: 98.2/100" in payload["final_report"]

    def test_generate_empty_topic_is_accepted(self):
        response = client.post(GENERATE_URL, json={"topic": ""})
        assert response.status_code == 200

    def test_generate_whitespace_topic_is_accepted(self):
        response = client.post(GENERATE_URL, json={"topic": "   "})
        assert response.status_code == 200

    def test_generate_unicode_topic_round_trips(self):
        response = client.post(GENERATE_URL, json={"topic": "ΘçÅσ¡ÉAI"})
        assert response.json()["topic"] == "ΘçÅσ¡ÉAI"

    def test_missing_body_returns_422(self):
        response = client.post(GENERATE_URL)
        assert response.status_code == 422

    def test_missing_topic_field_returns_422(self):
        response = client.post(GENERATE_URL, json={})
        assert response.status_code == 422

    def test_non_string_topic_returns_422(self):
        response = client.post(GENERATE_URL, json={"topic": 123})
        assert response.status_code == 422

    def test_unknown_route_returns_404(self):
        response = client.post("/api/v1/research/nope", json={"topic": "AI"})
        assert response.status_code == 404