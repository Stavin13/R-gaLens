from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import documents, timeline, search, analysis
from app.utils.logger import logger

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/ingestion", tags=["ingestion"])
app.include_router(timeline.router, prefix=f"{settings.API_V1_STR}/timeline", tags=["timeline"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["analysis"])
app.include_router(analysis.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["analysis_stats"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Musicology Research Assistant API...")

@app.get("/")
async def root():
    return {"message": "Welcome to the Musicology Research Assistant API"}
