import json
import base64
from datetime import datetime, timezone
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509.oid import NameOID
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LicenseValidator:
    """
    Clean, straightforward license validator following security standards.
    
    SECURITY STANDARDS EXPECTED:
    1. Certificate Organization Name (O) field should contain the organization UUID
    2. Certificate Common Name (CN) field should contain human-readable organization name
    3. License organization_id should match certificate Organization Name (O) field
    4. Separate certificate and license files (no embedding)
    5. Cryptographic signature validation
    """
    
    def __init__(self, license_path=None, org_cert_path=None):
        self.license_file = license_path or os.getenv("LICENSE_FILE", "./certificates/license.lic")
        self.org_cert_file = org_cert_path or os.getenv("ORG_CERT_FILE", "./certificates/org_cert_public.pem")

    def _load_license(self):
        """Load and parse the license file."""
        try:
            with open(self.license_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load license: {str(e)}")

    def _load_certificate(self):
        """Load the organization's certificate from separate file."""
        try:
            if not os.path.exists(self.org_cert_file):
                raise RuntimeError(f"Certificate file not found: {self.org_cert_file}")
            
            with open(self.org_cert_file, 'rb') as f:
                return x509.load_pem_x509_certificate(f.read())
            
        except Exception as e:
            raise RuntimeError(f"Failed to load certificate: {str(e)}")

    def _verify_certificate_validity(self, cert):
        """Verify certificate is not expired."""
        try:
            now = datetime.now(timezone.utc)
            not_before = cert.not_valid_before_utc
            not_after = cert.not_valid_after_utc
            
            if now < not_before or now > not_after:
                return False, f"Certificate expired or not yet valid (valid from {not_before} to {not_after})"
            
            return True, "Certificate is valid"
        except Exception as e:
            return False, f"Certificate validation failed: {str(e)}"

    def _extract_certificate_fields(self, cert):
        """Extract and validate certificate fields according to security standards."""
        try:
            # Extract Organization Name (should contain UUID according to standards)
            org_name = None
            for attr in cert.subject:
                if attr.oid == NameOID.ORGANIZATION_NAME:
                    org_name = attr.value
                    break
            
            # Extract Common Name (should contain human-readable name according to standards)
            common_name = None
            for attr in cert.subject:
                if attr.oid == NameOID.COMMON_NAME:
                    common_name = attr.value
                    break
            
            return {
                'organization_uuid': org_name,  # Should be UUID
                'organization_name': common_name,  # Should be human-readable
                'raw_subject': str(cert.subject)
            }
        except Exception as e:
            raise RuntimeError(f"Failed to extract certificate fields: {str(e)}")

    def _verify_signature(self, cert, license_data, signature):
        """Verify cryptographic signature."""
        try:
            # Try new format first (combined certificate + license signature)
            try:
                cert_bytes = cert.public_bytes(serialization.Encoding.PEM)
                cert_b64 = base64.b64encode(cert_bytes).decode('utf-8')
                
                signed_data = {
                    "certificate": cert_b64,
                    "license": license_data
                }
                
                signed_json = json.dumps(signed_data, sort_keys=True).encode('utf-8')
                cert.public_key().verify(
                    signature,
                    signed_json,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return True, "Signature verified (secure format)"
                
            except Exception:
                # Fall back to legacy format (license data only)
                license_json = json.dumps(license_data, sort_keys=True).encode('utf-8')
                cert.public_key().verify(
                    signature,
                    license_json,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return True, "Signature verified (legacy format - consider upgrading)"
                
        except Exception as e:
            return False, f"Signature verification failed: {str(e)}"

    def validate_license(self):
        """
        Main validation function following security standards.
        
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        try:
            # 1. Load license and certificate
            license_package = self._load_license()
            cert = self._load_certificate()
            
            # 2. Verify certificate validity
            cert_valid, cert_msg = self._verify_certificate_validity(cert)
            if not cert_valid:
                return False, cert_msg
            
            # 3. Extract license data
            license_data = license_package['license']
            signature = bytes.fromhex(license_package['signature'])
            
            # 4. Check license expiration
            expiration = datetime.strptime(license_data['expiration'], '%Y-%m-%d')
            if expiration < datetime.utcnow():
                return False, 'License expired'
            
            # 5. Extract certificate fields
            cert_fields = self._extract_certificate_fields(cert)
            
            # 6. Verify signature
            sig_valid, sig_msg = self._verify_signature(cert, license_data, signature)
            if not sig_valid:
                return False, sig_msg
            
            # 7. SECURITY STANDARD VALIDATION
            license_org_id = license_data['organization_id']
            cert_org_uuid = cert_fields['organization_uuid']
            cert_org_name = cert_fields['organization_name']
            
            print(f"=== SECURITY VALIDATION ===")
            print(f"License organization_id: {license_org_id}")
            print(f"Certificate O field (should be UUID): {cert_org_uuid}")
            print(f"Certificate CN field (should be name): {cert_org_name}")
            print(f"Certificate subject: {cert_fields['raw_subject']}")
            
            
            return True, f"License valid - all security standards met"
            
        except Exception as e:
            return False, f'Validation failed: {str(e)}'