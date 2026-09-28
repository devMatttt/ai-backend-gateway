from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest
from app.services.chat_service import event_stream_generator
from app.rag.retriever import search_similar_documents
from app.memory.tools import MEMORY_TOOL_SCHEMA, check_and_extract_memory  # Auto-memory tool call

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/stream")
async def stream_chat(request: ChatRequest):
    """Standard LLM token streaming route."""
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    return StreamingResponse(
        event_stream_generator(request.prompt, request.model),
        media_type="text/event-stream"
    )

@router.post("/rag")
async def stream_rag_chat(request: ChatRequest):
    """RAG-augmented streaming route with auto-memory extraction."""
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    # 1. Background memory auto-ingestion tool check
    await check_and_extract_memory(request.prompt)

    # 2. Vector search retrieval from pgvector
    context_chunks = await search_similar_documents(request.prompt, limit=2)
    context_str = "\n".join(f"- {c}" for c in context_chunks) if context_chunks else "No relevant context found."

    # 3. Construct Augmented Prompt
    augmented_prompt = f"""Use the following facts to answer the question:

Context:
{context_str}

Question: {request.prompt}
Answer:"""

    return StreamingResponse(
        event_stream_generator(augmented_prompt, request.model),
        media_type="text/event-stream"
    )