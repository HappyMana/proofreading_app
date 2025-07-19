from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.proofreading import router as proofreading_router

app = FastAPI(
    title="Proofreading API",
    description="Japanese Text Proofreading System API",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(proofreading_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Proofreading API",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}