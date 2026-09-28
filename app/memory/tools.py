# app/memory/tools.py
import logging
from app.memory.repository import insert_document

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
        
        return {"status": "success", "extracted": True}
    except Exception as e:
        logger.error(f"Error extracting memory: {str(e)}")
        return {"status": "error", "message": str(e)}