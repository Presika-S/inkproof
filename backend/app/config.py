import os


def _db_url() -> str:
    url = os.getenv("DATABASE_URL", "sqlite:///./inkproof.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Settings:
    database_url = _db_url()
    secret_key = os.getenv("SECRET_KEY", "dev-only-secret-change-me-0123456789abcdef")
    cors_origins = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5180,http://127.0.0.1:5180"
        ).split(",")
        if o.strip()
    ]

    seed_demo = os.getenv("SEED_DEMO", "true").lower() == "true"
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    ai_model = os.getenv("AI_MODEL", "claude-sonnet-5-5")
    token_hours = 12


settings = Settings()
