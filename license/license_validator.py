import json
import base64
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LicenseValidator:
    def __init__(self, license_path=None, ca_cert_path=None):
        self.license_file = license_path or os.getenv("LICENSE_FILE", "./certificates/license.lic")
        self.ca_cert_file = ca_cert_path or os.getenv("CA_CERT_FILE", "./certificates/ca_cert_public.pem")
        self.ca_cert = self._load_ca_cert()

    def _load_ca_cert(self):
        """Load the CA certificate."""
        try:
            with open(self.ca_cert_file, 'rb') as f:
                return x509.load_pem_x509_certificate(f.read())
        except Exception as e:
            raise RuntimeError(f"Failed to load CA certificate: {str(e)}")

    def _load_license(self):
        """Load the license file."""
        try:
            with open(self.license_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load license: {str(e)}")

    def _verify_certificate_chain(self, cert_data):
        """Verify the certificate chain against the CA."""
        try:
            # Load customer certificate from base64
            cert_bytes = base64.b64decode(cert_data)
            customer_cert = x509.load_pem_x509_certificate(cert_bytes)
            
            # Verify certificate was signed by our CA
            self.ca_cert.public_key().verify(
                customer_cert.signature,
                customer_cert.tbs_certificate_bytes,
                padding.PKCS1v15(),
                customer_cert.signature_hash_algorithm
            )
            
            # Verify certificate is not expired
            now = datetime.utcnow()
            if now < customer_cert.not_valid_before or now > customer_cert.not_valid_after:
                return False, "Certificate expired or not yet valid"
            
            return True, customer_cert
        except Exception as e:
            return False, f"Certificate validation failed: {str(e)}"

    def validate_license(self):
        """Core license validation logic."""
        try:
            # Load and parse license
            license_package = self._load_license()
            
            # Verify certificate
            cert_valid, cert_result = self._verify_certificate_chain(license_package['certificate'])
            if not cert_valid:
                return False, cert_result
            
            customer_cert = cert_result
            license_data = license_package['license']
            signature = bytes.fromhex(license_package['signature'])
            
            # Check license expiration
            expiration = datetime.strptime(license_data['expiration'], '%Y-%m-%d')
            if expiration < datetime.utcnow():
                return False, 'License expired'
            
            # Verify license signature using customer's public key
            license_json = json.dumps(license_data, sort_keys=True).encode('utf-8')
            customer_cert.public_key().verify(
                signature,
                license_json,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Extract customer ID from certificate
            cert_customer_id = None
            for attr in customer_cert.subject:
                if attr.oid == NameOID.SERIAL_NUMBER:
                    cert_customer_id = attr.value
                    break
            
            # Verify customer ID matches
            if cert_customer_id != license_data['customer_id']:
                return False, 'Customer ID mismatch'
            
            return True, 'License valid'
            
        except Exception as e:
            return False, f'Validation failed: {str(e)}' 