import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import init_db
from app.routers import jobs, resumes, candidates, screen, demo, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database tables and uploads directory exist on startup."""
    init_db()
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    yield


# Initialize FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    description="Production-Ready Smart Resume Screener API with Semantic Matching & Transparent 1-10 Scoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(candidates.router)
app.include_router(screen.router)
app.include_router(demo.router)
app.include_router(health.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global unhandled exception interceptor to return safe JSON errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred during processing. Please try again."
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
