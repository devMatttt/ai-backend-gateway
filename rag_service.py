import json
import asyncpg
from pgvector.asyncpg import register_vector
from ollama import AsyncClient

# Database connection settings matching docker-compose.yml
DB_CONFIG = {
    "user": "postgres",
    "password": "password",
    "database": "ai_memory",
    "host": "127.0.0.1",
    "port": 5432
}

ollama_client = AsyncClient()
EMBEDDING_MODEL = "nomic-embed-text"
# nomic-embed-text outputs 768-dimensional vectors
VECTOR_DIMENSIONS = 768 

async def get_db_connection():
    """Establishes an async connection to PostgreSQL and registers pgvector."""
    conn = await asyncpg.connect(**DB_CONFIG)
    # Enable vector extension in Postgres if not enabled
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    # Register the pgvector type converter for asyncpg
    await register_vector(conn)
    return conn

async def init_db():
    """Initializes the documents table with a vector column."""
    conn = await get_db_connection()
    try:
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector({VECTOR_DIMENSIONS})
            );
        """)
        # Create an HNSW index for fast approximate nearest neighbor search
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS knowledge_base_embedding_idx 
            ON knowledge_base USING hnsw (embedding vector_cosine_ops);
        """)
        print("✅ Database table and pgvector index initialized.")
    finally:
        await conn.close()

async def generate_embedding(text: str) -> list[float]:
    """Uses Ollama to convert text into a 768-dimensional float vector."""
    response = await ollama_client.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text
    )
    return response["embedding"]

async def insert_document(content: str):
    """Generates an embedding for a document and saves it into Postgres."""
    embedding = await generate_embedding(content)
    conn = await get_db_connection()
    try:
        await conn.execute(
            "INSERT INTO knowledge_base (content, embedding) VALUES ($1, $2)",
            content, embedding
        )
        print(f"📖 Inserted document into DB: '{content[:40]}...'")
    finally:
        await conn.close()

async def search_similar_documents(query: str, limit: int = 2) -> list[str]:
    """
    Converts query to an embedding and runs cosine similarity (<=>) search in Postgres.
    """
    query_embedding = await generate_embedding(query)
    conn = await get_db_connection()
    try:
        # PostgreSQL pgvector operator <=> calculates Cosine Distance
        # Ordering by distance ASC returns the most similar records first
        rows = await conn.fetch("""
            SELECT content, (embedding <=> $1) as distance
            FROM knowledge_base
            ORDER BY distance ASC
            LIMIT $2;
        """, query_embedding, limit)
        
        return [row["content"] for row in rows]
    finally:
        await conn.close()