from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
import os
from core.license_validator import LicenseValidator
import json
from dotenv import load_dotenv

load_dotenv()

LICENSE_FILE = os.getenv("LICENSE_FILE", "./license.lic")

app = FastAPI()
templates = Jinja2Templates(directory="webapp/templates")
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

validator = LicenseValidator()


def get_license_info():
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
    except Exception:
        return [], "-", "-"

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
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

@app.post("/upload-license")
async def upload_license(request: Request, file: UploadFile = File(...)):
    with open(LICENSE_FILE, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Redirect to home with the message as a query parameter
    return RedirectResponse(url=f"/?upload_result=License uploaded and checked.", status_code=200)

@app.get("/status")
def get_status():
    valid, message = validator.validate_license()
    modules, expiration, issued_on = get_license_info()
    return {"valid": valid, "message": message, "modules": modules, "expiration": expiration, "issued_on": issued_on} 