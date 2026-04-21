from fastapi import FastAPI
from tradingbot_edge.config import get_settings
from tradingbot_edge.api.v1 import router as v1_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered chart analysis using GPT-4V"
)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"service": settings.app_name, "version": settings.app_version, "status": "ok"}
