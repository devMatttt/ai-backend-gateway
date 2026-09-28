# import asyncpg
# from pgvector.asyncpg import register_vector
from app.config.settings import settings
from app.llm.embeddings import generate_embedding
from app.db.session import get_db_connection

# async def get_db_connection():
#     conn = await asyncpg.connect(**settings.db_config)
#     await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
#     await register_vector(conn)
#     return conn

async def search_similar_documents(query: str, limit: int = 2) -> list[str]:
    query_embedding = await generate_embedding(query)
    conn = await get_db_connection()
    try:
        rows = await conn.fetch("""
            SELECT content, (embedding <=> $1) as distance
            FROM knowledge_base
            ORDER BY distance ASC
            LIMIT $2;
        """, query_embedding, limit)
        return [row["content"] for row in rows]
    finally:
        await conn.close()