import asyncio
from rag_service import init_db, insert_document, search_similar_documents

async def main():
    print("1. Initializing DB Schema...")
    await init_db()

    print("\n2. Seeding Knowledge Base...")
    sample_docs = [
        "Project Orion is an async AI gateway built using FastAPI, Uvicorn, and Ollama.",
        "System administrators should reboot the main database cluster every Sunday at 02:00 UTC.",
        "The RTX 4060 Ti GPU features 16GB of VRAM and runs local LLM inference efficiently."
    ]
    
    for doc in sample_docs:
        await insert_document(doc)

    print("\n3. Testing Vector Search...")
    query = "What time is the database maintenance?"
    print(f"Query: '{query}'")
    
    matches = await search_similar_documents(query, limit=1)
    print("\nMatches retrieved from PostgreSQL:")
    for i, match in enumerate(matches, 1):
        print(f"[{i}] {match}")

if __name__ == "__main__":
    asyncio.run(main())