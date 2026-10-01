# app/memory/tools.py
import logging

logger = logging.getLogger(__name__)

from app.memory.repository import insert_document, search_similar_memories
from app.llm.embeddings import generate_embedding

MEMORY_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "save_user_memory",
        "description": "Saves persistent user facts, identity details, or long-term preferences into vector memory.",
        "parameters": {
            "type": "object",
            "properties": {
                "fact": {
                    "type": "string",
                    "description": "A clear, declarative statement of the fact (e.g., 'The user's name is Matt')."
                }
            },
            "required": ["fact"]
        }
    }
}

async def check_and_extract_memory(user_input: str, user_id: str = "default_user") -> dict:
    """
    Background memory auto-ingestion function.
    Extracts facts from user input and saves them to pgvector.
    """
    try:
        # Example logic: replace or call your LLM/schema logic here
        # If a fact is detected, persist it in vector storage:
        # await save_memory(user_id=user_id, content=user_input)

        """
        Generates embedding, checks if the fact already exists in vector DB,
        and inserts only if it is a new fact.
        """

        # 1. Generate the vector embedding for the extracted fact
        embedding = await generate_embedding(user_input)

        # 2. Search if a similar memory already exists (similarity >= 0.85)
        existing_memories = await search_similar_memories(
            user_id=user_id, 
            embedding=embedding, 
            threshold=0.85
        )

        if existing_memories:
            logger.info("user_input is in ai memory.")
        else:
            logger.info("%s is not in ai memory.", user_input)
        
        return {"status": "success", "extracted": True}
    except Exception as e:
        logger.error(f"Error extracting memory: {str(e)}")
        return {"status": "error", "message": str(e)}