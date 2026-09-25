from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AegisGraph"
    API_V1_STR: str = "/api/v1"

    # Comma-separated list of allowed frontend origins for CORS.
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Neo4j Settings
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str
    NEO4J_DATABASE: str = "aegisgraph"

    # LLM Settings
    LLM_PROVIDER: str = "ollama"
    
    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5-coder:7b"

    # Context Builder Settings
    MAX_RECORDS: int = 20
    MAX_CHUNK_CHARS: int = 1500
    MAX_CONTEXT_CHARS: int = 8000

    # Postgres Configuration
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:123456@localhost:5432/aegisgraph")

    # Security & Telemetry Settings
    # Server-only secret used to sign session tickets (role + session id).
    # Override in .env for any real deployment; the default is fine for local dev.
    SECURITY_SESSION_SECRET: str = "dev-insecure-change-me"

    # Research-aligned semantic drift model
    SECURITY_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    # Number of recent queries (including the current one) considered when
    # computing the semantic-focus signal (paper Eq. 1's sliding window W).
    SECURITY_SEMANTIC_WINDOW_SIZE: int = 5
    SECURITY_TEMPORAL_WINDOW_SECONDS: int = 60
    SECURITY_ALPHA_TEMP: float = 0.05
    SECURITY_TEMPORAL_THRESHOLD: int = 5
    SECURITY_GRAPH_MAX_DEPTH: int = 5
    SECURITY_GRAPH_MAX_NODES: int = 50
    SECURITY_GRAPH_WEIGHT: float = 0.5
    
    # Risk Fusion Weights (alpha, beta, gamma, delta)
    SECURITY_WEIGHT_SEMANTIC: float = 0.25
    SECURITY_WEIGHT_TEMPORAL: float = 0.25
    SECURITY_WEIGHT_ENTITY: float = 0.25
    SECURITY_WEIGHT_GRAPH: float = 0.25
    
    SECURITY_EWMA_LAMBDA: float = 0.4
    
    # Adaptive Response Policy Parameters
    SECURITY_THETA_MID: float = 0.55
    SECURITY_THETA_SLOPE: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
