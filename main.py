import os
import sys
import subprocess
import signal
from dotenv import load_dotenv

# Import logger
from helper.logger import setup_logger

# Load environment variables
load_dotenv()

# Configure logging
logger = setup_logger(name='process_manager')

def start_webapp():
    """Start the FastAPI web application."""
    try:
        # Get web host and port from environment variables
        web_host = os.getenv('WEB_HOST', '0.0.0.0')
        web_port = os.getenv('WEB_PORT', '8000')
        
        # Prepare uvicorn command
        uvicorn_cmd = [
            sys.executable, "-m", "uvicorn", 
            "webapp.main:app", 
            f"--host={web_host}", 
            f"--port={web_port}"
        ]
        
        logger.info(f"Starting webapp on {web_host}:{web_port}")
        
        # Start webapp
        webapp_process = subprocess.Popen(uvicorn_cmd)
        return webapp_process
    except Exception as e:
        logger.error(f"Failed to start web application: {e}")
        return None

def start_marshal_service():
    """Start the marshal service."""
    try:
        # Import here to avoid circular imports
        from core.marshal_service import MarshalService
        
        # Start marshal service
        marshal_service = MarshalService()
        marshal_thread = marshal_service.start()
        
        logger.info("Marshal service started.")
        return marshal_service, marshal_thread
    except Exception as e:
        logger.error(f"Failed to start marshal service: {e}")
        return None, None

def main():
    """Main entry point for the application."""
    try:
        # Start services
        webapp_process = start_webapp()
        marshal_service, marshal_thread = start_marshal_service()

        # Wait for webapp to complete (which it won't unless there's an error)
        if webapp_process:
            webapp_process.wait()
    except KeyboardInterrupt:
        logger.info("Received interrupt. Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Cleanup if needed
        if 'marshal_service' in locals() and marshal_service:
            marshal_service.stop()

if __name__ == "__main__":
    main() 