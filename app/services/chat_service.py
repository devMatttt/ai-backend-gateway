import json
from app.llm.ollama_client import ollama_client

async def event_stream_generator(prompt: str, model: str):
    """
    Async generator that yields tokens from Ollama as Server-Sent Events (SSE).
    """
    try:
        messages = [{"role": "user", "content": prompt}]
        
        async_stream = await ollama_client.chat(
            model=model,
            messages=messages,
            stream=True
        )
        
        async for chunk in async_stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                payload = json.dumps({"token": content})
                yield f"data: {payload}\n\n"
                
        yield "data: [DONE]\n\n"

    except Exception as e:
        error_payload = json.dumps({"error": str(e)})
        yield f"data: {error_payload}\n\n"