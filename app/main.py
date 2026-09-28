from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.api.routes import chat, memory
# from contextlib import asynccontextmanager
# from app.db.session import init_db

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Runs automatically on container / server boot
#     await init_db()
#     yield
#     # Cleanup logic (if any) goes here

app = FastAPI(
    title="Max AI - backend",
    description="High-throughput streaming API for local LLM inference."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach router modules
app.include_router(chat.router, prefix="/api/v1")
app.include_router(memory.router, prefix="/api/v1")

@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")

@app.get("/health")
async def health_check():
    return {"status": "online"}