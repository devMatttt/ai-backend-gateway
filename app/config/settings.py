import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Gateway"
    
    # Database Settings
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_NAME: str = os.getenv("DB_NAME", "ai_memory")
    DB_HOST: str = os.getenv("DB_HOST", "postgres")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    
    # Ollama Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    PRIMARY_MODEL: str = "qwen2.5:3b"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    VECTOR_DIMENSIONS: int = 768

    @property
    def db_config(self) -> dict:
        return {
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "database": self.DB_NAME,
            "host": self.DB_HOST,
            "port": self.DB_PORT,
        }

settings = Settings()