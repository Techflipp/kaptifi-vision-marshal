from fastapi import FastAPI
from dotenv import load_dotenv

from api.endpoints import router as api_routes
from helper.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger(name='marshal-api')

def create_app():
    """Create and configure the FastAPI application."""
    # Create FastAPI application
    app = FastAPI(
        title="Kaptifi Vision Marshal",
        description="License Management API",
        version="0.1.0"
    )

    # Health check endpoint
    @app.get("/")
    def health_check():
        """
        Basic service status endpoint.
        
        Returns:
        - Simple operational status
        """
        return {"status": "Marshal API Up & Running"}

    # Include API routes
    app.include_router(api_routes, prefix="/api/v1")

    # Log application startup
    logger.info("Marshal API initialized successfully")

    return app

# Create the app
app = create_app()