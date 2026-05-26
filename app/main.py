# nihongo_backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import conversation, heatmap, immersion, vocab
from app.middleware.auth import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Nihongo API starting up")
    yield
    # Shutdown
    print("Nihongo API shutting down")


app = FastAPI(
    title="Nihongo API",
    version="1.0.0",
    description="Backend for the Nihongo Japanese learning app",
    lifespan=lifespan,
)

# CORS — Flutter mobile app sends no Origin, web preview + future web app domains
ALLOWED_ORIGINS = [
    "http://localhost:4444",        # local web preview
    "http://localhost:8080",        # flutter web dev
    "https://nihongo.app",          # production web (future)
    "https://www.nihongo.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# Route registration
app.include_router(conversation.router, prefix="/conversation", tags=["conversation"])
app.include_router(heatmap.router,      prefix="/heatmap",      tags=["heatmap"])
app.include_router(immersion.router,    prefix="/immersion",    tags=["immersion"])
app.include_router(vocab.router,        prefix="/vocab",        tags=["vocab"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "nihongo-api"}
