from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

load_dotenv()

from .database import engine, Base
from .routers import tasks, notes, finance, ai_chat

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Minha Vida", description="Seu assistente pessoal inteligente")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/api")
app.include_router(notes.router, prefix="/api")
app.include_router(finance.router, prefix="/api")
app.include_router(ai_chat.router, prefix="/api")

frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))


@app.get("/health")
def health():
    return {"status": "ok", "app": "Minha Vida"}
