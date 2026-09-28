from app.llm.ollama_client import ollama_client
from app.config.settings import settings

async def generate_embedding(text: str) -> list[float]:
    """Generates a float vector using Ollama's embedding API."""
    response = await ollama_client.embeddings(
        model=settings.EMBEDDING_MODEL,
        prompt=text
    )
    return response["embedding"]