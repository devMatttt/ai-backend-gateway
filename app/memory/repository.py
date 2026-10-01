from app.rag.retriever import get_db_connection
from app.llm.embeddings import generate_embedding

import json

async def insert_document(content: str):
    """Generates an embedding and inserts the document into pgvector."""
    embedding = await generate_embedding(content)
    conn = await get_db_connection()
    try:
        await conn.execute(
            "INSERT INTO knowledge_base (content, embedding) VALUES ($1, $2)",
            content, embedding
        )
    finally:
        await conn.close()

async def search_similar_memories(user_id: str, embedding: list[float], limit: int = 3, threshold: float = 0.85):
    """
    Searches for existing user memories using cosine similarity.
    Returns memories with a similarity score greater than or equal to the threshold.
    """
    conn = await get_db_connection()
    try:
        
        # 1 - (embedding <=> $2) converts cosine distance to cosine similarity (0 to 1)
        query = """
            SELECT id, content, 1 - (embedding <=> $2::vector) AS similarity
            FROM memories
            WHERE user_id = $1 AND (1 - (embedding <=> $2::vector)) >= $3
            ORDER BY similarity DESC
            LIMIT $4;
        """
        rows = await conn.fetch(query, user_id, embedding, threshold, limit)
        return [dict(row) for row in rows]
    finally:
        await conn.close()