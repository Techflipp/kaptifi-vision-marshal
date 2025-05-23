from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import json

from helper.logger import setup_logger
from license.license_validator import LicenseValidator

logger = setup_logger(name='marshal-endpoints')
router = APIRouter()
validator = LicenseValidator()

class LicenseInfo(BaseModel):
    """Structured response for license information."""
    valid: bool
    message: str
    customer_id: Optional[str] = None
    modules: Optional[List[str]] = []
    issued_on: str
    expiration: str
    
    

@router.get("/license", response_model=LicenseInfo)
def get_license_status():
    """
    Retrieve current license status.
    
    Returns:
    - Validation status
    - License details
    """
    try:
        # Validate license
        valid, message = validator.validate_license()
        
        # Get license file path
        license_file = os.getenv("LICENSE_FILE", "./certificates/license.lic")
        
        # Read license file
        with open(license_file, "r") as f:
            license_package = json.load(f)
        
        # Extract license data
        license_data = license_package.get("license", {})
        
        # Prepare response
        return LicenseInfo(
            valid=valid,
            message=message,
            customer_id=license_data.get("customer_id"),
            modules=license_data.get("modules", []),
            issued_on=str(license_data.get("issued_on", "-")),
            expiration=str(license_data.get("expiration", "-"))
        )
    
    except FileNotFoundError:
        logger.error("License file not found")
        raise HTTPException(status_code=404, detail="License file not found")
    
    except json.JSONDecodeError:
        logger.error("Invalid license file format")
        raise HTTPException(status_code=500, detail="Invalid license file format")
    
    except Exception as e:
        logger.error(f"Unexpected error retrieving license status: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving license status: {str(e)}") 