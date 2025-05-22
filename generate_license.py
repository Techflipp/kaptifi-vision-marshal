import json
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Load your private key
with open("marshal_private.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Fill in your license data
license_data = {
    "customer_id": "customer001",
    "customer_email": ["customer@example.com", "admin@example.com"],
    "modules": ["counting", "demographics"],
    "issued_on":"22-05-2025",
    "expiration": "22-05-2026"
}

# Create the signature
license_json = json.dumps(license_data, sort_keys=True).encode("utf-8")
signature = private_key.sign(
    license_json,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

license_package = {
    "license": license_data,
    "signature": signature.hex()
}

# Write to license.lic
with open("license.lic", "w") as f:
    json.dump(license_package, f, indent=2)

print("license.lic generated successfully.")