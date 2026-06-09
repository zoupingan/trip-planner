from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import trip, poi, map
from app.config import settings, get_settings

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trip.router, prefix="/api")
app.include_router(poi.router, prefix="/api")

app.include_router(map.router, prefix="/api")


@app.get("/health")
async def health():
    return {
        "service": settings.app_name,
        "version": settings.app_version
    }
