from app.config.settings import settings
import asyncpg
from pgvector.asyncpg import register_vector

# app/db/session.py
VECTOR_DIMENSIONS = 768

async def get_db_connection():
    conn = await asyncpg.connect(**settings.db_config)
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    await register_vector(conn)
    return conn

async def init_db():
    """Initializes extension, knowledge_base, and memories tables with indexes."""
    conn = await get_db_connection()
    try:
        # Enable vector extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Create knowledge_base table
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector({VECTOR_DIMENSIONS}),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Create knowledge_base HNSW index
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS knowledge_base_embedding_idx
            ON knowledge_base USING hnsw (embedding vector_cosine_ops);
        """)

        # Create memories table
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS memories (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL DEFAULT 'default_user',
                content TEXT NOT NULL,
                embedding vector({VECTOR_DIMENSIONS}),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Create memories HNSW index
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS memories_embedding_idx
            ON memories USING hnsw (embedding vector_cosine_ops);
        """)

        print("✅ Database tables (knowledge_base, memories) and pgvector indexes initialized successfully.")
    finally:
        await conn.close()