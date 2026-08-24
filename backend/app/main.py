from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.api.retrieval import router as retrieval_router
from app.core.config import settings

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(chat_router, prefix=settings.API_V1_STR, tags=["chat"])
# Removed to prevent security bypass: app.include_router(retrieval_router, prefix=settings.API_V1_STR, tags=["retrieval"])

@app.get("/")
async def root():
    return {"message": "Welcome to AegisGraph API"}
