from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AegisGraph"
    API_V1_STR: str = "/api/v1"

    # Neo4j Settings
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str
    NEO4J_DATABASE: str = "aegisgraph"

    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5-coder:7b"

    # Context Builder Settings
    MAX_RECORDS: int = 20
    MAX_CHUNK_CHARS: int = 1500
    MAX_CONTEXT_CHARS: int = 8000

    # Security & Telemetry Settings
    # Research-aligned semantic drift model
    SECURITY_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    SECURITY_TEMPORAL_WINDOW_SECONDS: int = 60
    SECURITY_ALPHA_TEMP: float = 0.1
    SECURITY_TEMPORAL_THRESHOLD: int = 5
    SECURITY_GRAPH_MAX_DEPTH: int = 5
    SECURITY_GRAPH_MAX_NODES: int = 50
    SECURITY_GRAPH_WEIGHT: float = 0.5
    
    # Risk Fusion Weights (alpha, beta, gamma, delta)
    SECURITY_WEIGHT_SEMANTIC: float = 0.25
    SECURITY_WEIGHT_TEMPORAL: float = 0.25
    SECURITY_WEIGHT_ENTITY: float = 0.25
    SECURITY_WEIGHT_GRAPH: float = 0.25
    
    SECURITY_EWMA_LAMBDA: float = 0.3
    
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
