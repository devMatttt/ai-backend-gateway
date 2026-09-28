import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ollama import AsyncClient

app = FastAPI(
    title="Async AI Backend Gateway",
    description="High-throughput streaming API for local LLM inference."
)

# Enable CORS for frontend clients (React, Next.js, Vue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the non-blocking async client
ollama_client = AsyncClient()

class ChatRequest(BaseModel):
    prompt: str
    model: str = "qwen2.5:3b"

async def event_stream_generator(prompt: str, model: str):
    """
    Async generator that yields tokens from the GPU as Server-Sent Events (SSE).
    """
    try:
        messages = [{"role": "user", "content": prompt}]
        
        # Request an async stream from the model engine
        async_stream = await ollama_client.chat(
            model=model,
            messages=messages,
            stream=True
        )
        
        async for chunk in async_stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                # Format payload according to the SSE specification
                payload = json.dumps({"token": content})
                yield f"data: {payload}\n\n"
                
        # Signal completion to the client
        yield "data: [DONE]\n\n"

    except Exception as e:
        error_payload = json.dumps({"error": str(e)})
        yield f"data: {error_payload}\n\n"

@app.post("/api/v1/chat/stream")
async def stream_chat(request: ChatRequest):
    """
    HTTP POST endpoint that streams LLM tokens asynchronously.
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    return StreamingResponse(
        event_stream_generator(request.prompt, request.model),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    # Run server on port 8000 with auto-reload enabled
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)