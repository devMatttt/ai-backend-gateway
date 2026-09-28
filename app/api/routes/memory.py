from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.memory.repository import insert_document

router = APIRouter(prefix="/memory", tags=["Memory"])

class MemoryRequest(BaseModel):
    content: str

router = APIRouter()

@router.post("")
async def add_memory(request: MemoryRequest):
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty.")
    
    await insert_document(request.content)
    return {"status": "success", "message": "Memory successfully saved to vector storage."}