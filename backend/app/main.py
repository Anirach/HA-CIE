"""Main FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import auth, causal, graph, hospitals, assessments, dashboard, simulations, timeline, insights, reports, digital_health, isqua

app = FastAPI(
    title=settings.app_name,
    description="API for hospital accreditation analytics and causal inference",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3500",
        "http://127.0.0.1:3500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(causal.router, prefix="/api/v1")
app.include_router(graph.router, prefix="/api/v1")
app.include_router(hospitals.router, prefix="/api/v1")
app.include_router(assessments.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(simulations.router, prefix="/api/v1")
app.include_router(timeline.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(digital_health.router, prefix="/api/v1")
app.include_router(isqua.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "storage_mode": settings.storage_mode,
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to HA-CIE API",
        "docs_url": "/docs",
    }
