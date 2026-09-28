import json
import asyncpg
import os
from pgvector.asyncpg import register_vector
from ollama import AsyncClient

# 1. Read DB connection settings from environment variables with Docker-aware fallbacks
DB_CONFIG = {
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "database": os.getenv("DB_NAME", "ai_memory"),
    "host": os.getenv("DB_HOST", "postgres"),  # Points to 'postgres' container service name
    "port": int(os.getenv("DB_PORT", 5432))
}

# 2. Ollama connection setup with host.docker.internal fallback
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
ollama_client = AsyncClient(host=OLLAMA_URL)

EMBEDDING_MODEL = "nomic-embed-text"
VECTOR_DIMENSIONS = 768 

async def get_db_connection():
    """Establishes an async connection to PostgreSQL and registers pgvector."""
    conn = await asyncpg.connect(**DB_CONFIG)
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    await register_vector(conn)
    return conn

async def init_db():
    """Initializes the knowledge_base table with an HNSW vector index."""
    conn = await get_db_connection()
    try:
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector({VECTOR_DIMENSIONS})
            );
        """)
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
    Ensures table exists, converts query to an embedding, and runs cosine search.
    """
    # Auto-initialize DB schema if it doesn't exist yet
    try:
        conn = await get_db_connection()
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise e

    try:
        # Check if table exists; if not, initialize and seed sample data
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'knowledge_base'
            );
        """)
        
        if not table_exists:
            print("⚙️ Table 'knowledge_base' not found. Initializing database...")
            await conn.close()
            await init_db()
            await seed_initial_knowledge()
            conn = await get_db_connection()

        query_embedding = await generate_embedding(query)

        rows = await conn.fetch("""
            SELECT content, (embedding <=> $1) as distance
            FROM knowledge_base
            ORDER BY distance ASC
            LIMIT $2;
        """, query_embedding, limit)
        
        return [row["content"] for row in rows]
    finally:
        await conn.close()

async def seed_initial_knowledge():
    """Seeds sample documents into the vector database for testing."""
    sample_docs = [
        "System administrators should reboot the main database cluster every Sunday at 02:00 UTC.",
        "The AI Gateway API handles asynchronous token streaming using Server-Sent Events (SSE).",
        "PostgreSQL pgvector extension uses HNSW indexing for fast vector similarity searches."
    ]
    for doc in sample_docs:
        await insert_document(doc)
    print("🌱 Initial knowledge base successfully seeded!")