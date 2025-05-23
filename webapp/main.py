from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import logging

# Import routes
from .routes import router as web_routes
from .api import router as api_routes

# Import logger from helper
from helper.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logger for webapp
logger = setup_logger(name='webapp')

def create_app():
    """Create and configure the FastAPI application."""
    # Create FastAPI application
    app = FastAPI(
        title="Kaptifi Vision Marshal",
        description="License Management Web Interface",
        version="0.1.0"
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

    # Include routers
    app.include_router(web_routes)
    app.include_router(api_routes)

    # Log application startup
    logger.info("Webapp initialized successfully")

    return app

# Create the app
app = create_app()