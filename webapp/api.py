from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import shutil
from license.license_validator import LicenseValidator
from dotenv import load_dotenv

# Import logger
from helper.logger import setup_logger

# Load environment variables
load_dotenv()

# Get license file path from environment
LICENSE_FILE = os.getenv("LICENSE_FILE", "./license.lic")

# Create a router for API routes
router = APIRouter(prefix="/api/v1")

# Initialize logger
logger = setup_logger(name='webapp_api')

# Initialize validator
validator = LicenseValidator()

class LicenseInfo(BaseModel):
    """Structured response for license information."""
    valid: bool
    message: str
    modules: Optional[List[str]] = []
    expiration: str
    issued_on: str

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
        raise HTTPException(status_code=500, detail=f"Error reading license: {str(e)}")

@router.get("/license", response_model=LicenseInfo)
def get_license_status():
    """Get current license status."""
    try:
        valid, message = validator.validate_license()
        modules, expiration, issued_on = get_license_info()
        
        logger.info(f"License status requested - Valid: {valid}")
        
        return LicenseInfo(
            valid=valid,
            message=message,
            modules=modules,
            expiration=expiration,
            issued_on=issued_on
        )
    except Exception as e:
        logger.error(f"Error retrieving license status: {e}")
        raise

@router.post("/license/upload")
async def upload_license(file: UploadFile = File(...)):
    """Upload a new license file."""
    try:
        # Log the upload attempt
        logger.info("License upload API endpoint called")
        
        # Save the uploaded file
        with open(LICENSE_FILE, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Log successful file save
        logger.info("License file saved successfully")
        
        # Validate the uploaded license
        valid, message = validator.validate_license()
        
        # Log validation result
        logger.info(f"Uploaded license validation result - Valid: {valid}")
        
        return {
            "success": valid,
            "message": message
        }
    except Exception as e:
        # Log any errors during upload
        logger.error(f"Error during license upload: {e}")
        raise HTTPException(status_code=400, detail=f"Error uploading license: {str(e)}") 