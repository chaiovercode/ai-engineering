from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import transform_router, chart_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Transform IC research reports into LinkedIn posts, newsletter snippets, and WhatsApp messages",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transform_router)
app.include_router(chart_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
