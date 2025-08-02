from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.recommendations import router as rec_router, initialize_services
from app.core.logging_config import setup_logging, get_logger
from app.db.database import test_connection

# Setup logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="ML Post Recommender",
    description="Microservice for recommending posts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting ML Post Recommender service")

    try:
        # Test database connection
        logger.info("Testing database connection")
        if not test_connection():
            raise Exception("Database connection failed")

        # Initialize recommendation services
        logger.info("Initializing recommendation services")
        initialize_services()

        logger.info("Service startup completed successfully")

    except Exception as e:
        logger.error(f"Service startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down ML Post Recommender service")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        if not test_connection():
            raise HTTPException(
                status_code=503, detail="Database connection failed")

        return {"status": "healthy", "message": "Service is running"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Include routers
app.include_router(rec_router, prefix="/api/v1", tags=["recommendations"])
