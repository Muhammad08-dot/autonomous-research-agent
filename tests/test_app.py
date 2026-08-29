from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


class TestAppHealth:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_status_payload(self):
        response = client.get("/health")
        body = response.json()
        assert body["status"] == "healthy"
        assert body["service"] == settings.PROJECT_NAME

    def test_health_response_headers(self):
        response = client.get("/health")
        assert response.headers["content-type"].startswith("application/json")


class TestAppSchema:
    def test_app_title(self):
        assert app.title == settings.PROJECT_NAME

    def test_docs_and_openapi_urls_configured(self):
        assert app.docs_url == "/docs"
        assert app.openapi_url == f"{settings.API_V1_STR}/openapi.json"

    def test_openapi_contains_health_route(self):
        schema = client.get(app.openapi_url).json()
        assert "/health" in schema["paths"]

    def test_openapi_contains_research_generate_route(self):
        schema = client.get(app.openapi_url).json()
        assert "/api/v1/research/generate" in schema["paths"]

    def test_openapi_contains_metrics_route(self):
        schema = client.get(app.openapi_url).json()
        assert "/metrics" in schema["paths"]

    def test_research_generate_is_post_only(self):
        schema = client.get(app.openapi_url).json()
        assert "post" in schema["paths"]["/api/v1/research/generate"]