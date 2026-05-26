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

# CORS — allow Flutter app origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down to your domain in production
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registration
app.include_router(conversation.router, prefix="/conversation", tags=["conversation"])
app.include_router(heatmap.router,      prefix="/heatmap",      tags=["heatmap"])
app.include_router(immersion.router,    prefix="/immersion",    tags=["immersion"])
app.include_router(vocab.router,        prefix="/vocab",        tags=["vocab"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "nihongo-api"}
