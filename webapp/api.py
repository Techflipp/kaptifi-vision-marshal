from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
import os
from core.license_validator import LicenseValidator
import json

app = FastAPI()
templates = Jinja2Templates(directory="webapp/templates")
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

validator = LicenseValidator("webapp/config.yaml")


def get_license_info():
    try:
        with open("./license.lic", "r") as f:
            license_package = json.load(f)
        license_data = license_package["license"]
        modules = license_data.get("modules", [])
        expiration = license_data.get("expiration", "-")
        if not isinstance(expiration, str):
            expiration = str(expiration)
        return modules, expiration
    except Exception:
        return [], "-"

@app.get("/", response_class=HTMLResponse)
def home(request: Request, upload_result: str = None):
    valid, message = validator.validate_license()
    modules, expiration = get_license_info()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "valid": valid,
            "message": message,
            "upload_result": upload_result,
            "modules": modules,
            "expiration": expiration
        }
    )

@app.post("/upload_license", response_class=HTMLResponse)
async def upload_license(request: Request, file: UploadFile = File(...)):
    with open("./license.lic", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    valid, message = validator.validate_license()
    modules, expiration = get_license_info()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "valid": valid,
            "message": message,
            "upload_result": "License uploaded and checked.",
            "modules": modules,
            "expiration": expiration
        }
    )

@app.get("/status")
def get_status():
    valid, message = validator.validate_license()
    modules, expiration = get_license_info()
    return {"valid": valid, "message": message, "modules": modules, "expiration": expiration} 