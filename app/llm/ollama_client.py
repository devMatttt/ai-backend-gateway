from ollama import AsyncClient
from app.config.settings import settings

ollama_client = AsyncClient(host=settings.OLLAMA_BASE_URL)