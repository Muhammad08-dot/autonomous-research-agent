from app.core.config import Settings


class TestSettingsDefaults:
    def test_project_name_default(self):
        settings = Settings(_env_file=None)
        assert settings.PROJECT_NAME == "Self-Improving Autonomous Research Agent"

    def test_api_v1_str_default(self):
        settings = Settings(_env_file=None)
        assert settings.API_V1_STR == "/api/v1"

    def test_environment_default(self):
        settings = Settings(_env_file=None)
        assert settings.ENVIRONMENT == "development"

    def test_secret_key_default_present(self):
        settings = Settings(_env_file=None)
        assert isinstance(settings.SECRET_KEY, str)
        assert len(settings.SECRET_KEY) > 0

    def test_cors_origins_defaults(self):
        settings = Settings(_env_file=None)
        assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS
        assert "http://localhost:8006" in settings.BACKEND_CORS_ORIGINS

    def test_database_url_default_is_asyncpg(self):
        settings = Settings(_env_file=None)
        assert settings.DATABASE_URL.startswith("postgresql+asyncpg://")

    def test_redis_and_qdrant_defaults(self):
        settings = Settings(_env_file=None)
        assert settings.REDIS_URL.startswith("redis://")
        assert settings.QDRANT_URL.startswith("http://localhost:")

    def test_serializable_cors_origins_for_middleware(self):
        settings = Settings(_env_file=None)
        assert all(isinstance(origin, str) for origin in settings.BACKEND_CORS_ORIGINS)


class TestSettingsEnvironmentOverrides:
    def test_environment_variables_override_defaults(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "Custom Research Agent")
        monkeypatch.setenv("ENVIRONMENT", "production")
        settings = Settings(_env_file=None)
        assert settings.PROJECT_NAME == "Custom Research Agent"
        assert settings.ENVIRONMENT == "production"

    def test_json_list_env_for_cors(self, monkeypatch):
        monkeypatch.setenv("BACKEND_CORS_ORIGINS", '["http://custom.com"]')
        settings = Settings(_env_file=None)
        assert settings.BACKEND_CORS_ORIGINS == ["http://custom.com"]

    def test_single_value_env_for_cors(self, monkeypatch):
        monkeypatch.setenv("BACKEND_CORS_ORIGINS", '["http://only.com"]')
        settings = Settings(_env_file=None)
        assert settings.BACKEND_CORS_ORIGINS == ["http://only.com"]

    def test_extra_env_fields_ignored(self, monkeypatch):
        monkeypatch.setenv("UNRELATED_VAR", "should be ignored")
        settings = Settings(_env_file=None)
        assert settings.ENVIRONMENT == "development"