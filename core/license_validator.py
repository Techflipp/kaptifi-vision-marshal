import json
import yaml
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

class LicenseValidator:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.license_file = self.config['license_file']
        self.public_key_file = self.config['public_key_file']
        self.public_key = self._load_public_key()

    def _load_public_key(self):
        with open(self.public_key_file, 'rb') as f:
            return serialization.load_pem_public_key(f.read(), backend=default_backend())

    def _load_license(self):
        with open(self.license_file, 'r') as f:
            license_package = json.load(f)
        return license_package

    def validate_license(self):
        license_package = self._load_license()
        license_data = license_package['license']
        signature = bytes.fromhex(license_package['signature'])
        # Check expiration (now expects dd-mm-yyyy)
        expiration = datetime.strptime(license_data['expiration'], '%d-%m-%Y')
        if expiration < datetime.utcnow():
            return False, 'License expired'
        # Accept customer_email as list or string
        customer_email = license_data.get('customer_email')
        if isinstance(customer_email, str):
            customer_email = [customer_email]
        # (Optional) Add logic here if you want to check for a specific email
        # Verify signature
        license_json = json.dumps(license_data, sort_keys=True).encode('utf-8')
        try:
            self.public_key.verify(
                signature,
                license_json,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except Exception as e:
            return False, f'Signature verification failed: {e}'
        return True, 'License valid' 