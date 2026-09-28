from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str
    model: str = "qwen2.5:3b"