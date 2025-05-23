import json
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LicenseValidator:
    def __init__(self, license_path=None, public_key_path=None):
        self.license_file = license_path or os.getenv("LICENSE_FILE", "./config/kaptifi-vision-license.lic")
        self.public_key_file = public_key_path or os.getenv("PUBLIC_KEY_FILE", "./config/marshal_public.pem")
        self.public_key = self._load_public_key()

    def _load_public_key(self):
        try:
            with open(self.public_key_file, 'rb') as f:
                return serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
        except Exception as e:
            raise RuntimeError(f"Failed to load public key: {str(e)}")

    def _load_license(self):
        try:
            with open(self.license_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load license: {str(e)}")

    def validate_license(self):
        """Core license validation logic"""
        try:
            license_package = self._load_license()
            license_data = license_package['license']
            signature = bytes.fromhex(license_package['signature'])
            
            # Check expiration
            expiration = datetime.strptime(license_data['expiration'], '%d-%m-%Y')
            if expiration < datetime.utcnow():
                return False, 'License expired'
                
            # Verify signature
            license_json = json.dumps(license_data, sort_keys=True).encode('utf-8')
            self.public_key.verify(
                signature,
                license_json,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True, 'License valid'
        except Exception as e:
            return False, f'Validation failed: {str(e)}' 