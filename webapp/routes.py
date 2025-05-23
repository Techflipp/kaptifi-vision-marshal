from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import shutil
import os
import json
from dotenv import load_dotenv

# Import logger
from helper.logger import setup_logger

# Import validator
from core.license_validator import LicenseValidator

# Load environment variables
load_dotenv()

# Get license file path from environment
LICENSE_FILE = os.getenv("LICENSE_FILE", "./license.lic")

# Create a router for web routes
router = APIRouter()

# Setup templates
templates = Jinja2Templates(directory="webapp/templates")

# Initialize logger
logger = setup_logger(name='webapp_routes')

# Initialize validator
validator = LicenseValidator()

def get_license_info():
    """Helper function to extract license information."""
    try:
        with open(LICENSE_FILE, "r") as f:
            license_package = json.load(f)
        license_data = license_package["license"]
        modules = license_data.get("modules", [])
        expiration = license_data.get("expiration", "-")
        issued_on = license_data.get("issued_on", "-")
        if not isinstance(expiration, str):
            expiration = str(expiration)
        if not isinstance(issued_on, str):
            issued_on = str(issued_on)
        return modules, expiration, issued_on
    except Exception as e:
        logger.error(f"Error reading license file: {e}")
        return [], "-", "-"

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Render the home page with license information."""
    try:
        upload_result = request.query_params.get("upload_result")
        valid, message = validator.validate_license()
        modules, expiration, issued_on = get_license_info()    
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "valid": valid,
                "message": message,
                "upload_result": upload_result,
                "modules": modules,
                "expiration": expiration,
                "issued_on": issued_on
            }
        )
    except Exception as e:
        logger.error(f"Error rendering home page: {e}")
        raise

@router.post("/upload-license")
async def upload_license(request: Request, file: UploadFile = File(...)):
    """Handle license file upload."""
    try:
        # Validate file
        if not file.filename:
            return RedirectResponse(url="/?upload_result=No file selected.", status_code=303)
        
        # Check file extension
        if not file.filename.lower().endswith('.lic'):
            return RedirectResponse(url="/?upload_result=Invalid file type. Please upload a .lic file.", status_code=303)
        
        # Save the uploaded file
        with open(LICENSE_FILE, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate the license
        try:
            valid, message = validator.validate_license()
            if not valid:
                return RedirectResponse(url=f"/?upload_result=Invalid license: {message}", status_code=303)
        except Exception as e:
            return RedirectResponse(url="/?upload_result=License validation failed.", status_code=303)
        
        # Redirect to home with success message
        return RedirectResponse(url="/?upload_result=License uploaded and validated successfully.", status_code=303)
    
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error during license upload: {e}")
        return RedirectResponse(url="/?upload_result=Upload failed. Please try again.", status_code=303) 