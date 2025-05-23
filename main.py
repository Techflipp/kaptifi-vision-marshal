import os
import sys
import subprocess
import signal
import threading
import time
from dotenv import load_dotenv

# Import logger
from helper.logger import setup_logger

# Import license service
from license.license_manager import LicenseService

# Load environment variables
load_dotenv()

# Configure logging
logger = setup_logger(name='process_manager')

# Global variables to track processes
webapp_process = None
license_service = None
license_thread = None
stop_event = threading.Event()

def terminate_process(process, name):
    """Terminate a given process with logging and error handling."""
    if not process:
        return

    try:
        # Send termination signal
        if hasattr(process, 'terminate'):
            logger.info(f"Terminating {name} process...")
            process.terminate()
        
        # Wait for process to exit
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            logger.warning(f"Forcefully killing {name} process...")
            if hasattr(process, 'kill'):
                process.kill()
        
        # Additional check for subprocess
        if isinstance(process, subprocess.Popen):
            if process.poll() is None:
                logger.error(f"{name} process did not terminate.")
    except Exception as e:
        logger.error(f"Error terminating {name} process: {e}")

def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown."""
    logger.info("Received shutdown signal. Initiating clean shutdown...")
    stop_event.set()

def start_webapp():
    """Start the FastAPI web application."""
    global webapp_process
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
        
        # Start webapp with additional process group
        webapp_process = subprocess.Popen(
            uvicorn_cmd, 
            start_new_session=True  # Create a new process group
        )
        return webapp_process
    except Exception as e:
        logger.error(f"Failed to start web application: {e}")
        return None

def start_license_service():
    """Start the license service."""
    global license_service, license_thread
    try:
        # Start license service
        license_service = LicenseService()
        license_thread = license_service.start()
        
        logger.info("License service started.")
        return license_service, license_thread
    except Exception as e:
        logger.error(f"Failed to start license service: {e}")
        return None, None

def shutdown_services():
    """Gracefully shut down all services."""
    global webapp_process, license_service, license_thread
    
    # Stop webapp process
    terminate_process(webapp_process, "Webapp")
    
    # Stop license service
    if license_service:
        try:
            logger.info("Stopping license service...")
            license_service.stop()
            
            # Wait for thread to finish
            if license_thread and license_thread.is_alive():
                license_thread.join(timeout=3)
        except Exception as e:
            logger.error(f"Error stopping license service: {e}")

def main():
    """Main entry point for the application."""
    global webapp_process, license_service, license_thread
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start services
        webapp_process = start_webapp()
        license_service, license_thread = start_license_service()

        # Wait for stop event or process completion
        while not stop_event.is_set():
            if webapp_process and webapp_process.poll() is not None:
                logger.warning("Webapp process unexpectedly terminated.")
                break
            stop_event.wait(1)  # Check every second
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    finally:
        # Ensure clean shutdown
        shutdown_services()
        logger.info("Application shutdown complete.")
        
        # Force exit to release terminal
        os._exit(0)

if __name__ == "__main__":
    main() 