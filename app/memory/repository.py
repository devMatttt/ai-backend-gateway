from app.rag.retriever import get_db_connection
from app.llm.embeddings import generate_embedding

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