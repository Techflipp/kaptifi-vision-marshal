import json
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import os

def generate_license(customer_cert_path, customer_key_path, license_data):
    """Generate a signed license using customer's certificate."""
    
    # Load customer's certificate
    with open(customer_cert_path, "rb") as f:
        customer_cert = x509.load_pem_x509_certificate(f.read())
    
    # Load customer's private key
    with open(customer_key_path, "rb") as f:
        customer_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    
    # Prepare license package
    license_package = {
        "certificate": base64.b64encode(
            customer_cert.public_bytes(serialization.Encoding.PEM)
        ).decode('utf-8'),
        "license": {
            "customer_id": license_data["customer_id"],
            "modules": license_data["modules"],
            "issued_on": datetime.utcnow().strftime("%Y-%m-%d"),
            "expiration": license_data["expiration"]
        }
    }
    
    # Sign the license data
    license_json = json.dumps(license_package["license"], sort_keys=True).encode("utf-8")
    signature = customer_key.sign(
        license_json,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    # Add signature to package
    license_package["signature"] = signature.hex()
    
    return license_package

if __name__ == "__main__":
    # Example license data
    license_data = {
        "customer_id": "LIC-2024-001",  # Must match the certificate's license_id
        "modules": ["counting", "demographics"],
        "expiration": "2025-12-31"
    }
    
    # Certificate paths
    cert_dir = "certificates"
    customer_cert = os.path.join(cert_dir, "customer_public_cert.pem")
    customer_key = os.path.join(cert_dir, "customer_private_key.pem")
    
    # Generate license using customer certificate
    license_package = generate_license(
        customer_cert,
        customer_key,
        license_data
    )
    
    # Save the license
    output_file = os.path.join(cert_dir, "license.lic")
    
    with open(output_file, "w") as f:
        json.dump(license_package, f, indent=2)
    
    print(f"License generated successfully: {output_file}")
    print("\nCustomer package ready in: {cert_dir}")
    print("Files to ship to customer:")
    print("- customer_public_cert.pem (Customer's public certificate)")
    print("- customer_private_key.pem (Customer's private key)")
    print("- license.lic (Customer's license file)")