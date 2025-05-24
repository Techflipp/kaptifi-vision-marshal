from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import os

def generate_ca(cert_dir):
    """Generate CA private key and certificate."""
    # Generate CA private key
    ca_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )

    # Create CA certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "SA"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Riyadh"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Kaptifi"),
    ])

    ca_cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        ca_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)  # 1 year
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True
    ).sign(ca_key, hashes.SHA256())

    # Save CA private key (keep this secure!)
    with open(os.path.join(cert_dir, "ca_private_key.pem"), "wb") as f:
        f.write(ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Save CA certificate
    with open(os.path.join(cert_dir, "ca_cert_public.pem"), "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    return ca_key, ca_cert

def generate_customer_certificate(ca_key, ca_cert, customer_info, cert_dir):
    """Generate customer certificate signed by CA."""
    # Generate customer key pair
    customer_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Create certificate
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, customer_info.get('country', 'SA')),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, customer_info['organization_name']),
        x509.NameAttribute(NameOID.SERIAL_NUMBER, customer_info['organization_id'])
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        customer_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)  # 1 year
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True
    ).sign(ca_key, hashes.SHA256())

    # Save customer private key
    with open(os.path.join(cert_dir, "customer_private_key.pem"), "wb") as f:
        f.write(customer_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Save customer certificate
    with open(os.path.join(cert_dir, "customer_public_cert.pem"), "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    return customer_key, cert

if __name__ == "__main__":
    # Get the absolute path to the root directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    cert_dir = os.path.join(root_dir, "certificates")
    
    # Create certificates directory if it doesn't exist
    os.makedirs(cert_dir, exist_ok=True)
    print(f"Using certificates directory: {cert_dir}")

    # Generate CA
    print("Generating CA certificate...")
    ca_key, ca_cert = generate_ca(cert_dir)

    # Example customer
    customer_info = {
        "organization_name": "Example Corporation",
        "country": "SA",
        "organization_id": "611bac12-becd-45fa-b55d-e233650f4d54"
    }

    # Generate customer certificate
    print("Generating customer certificate...")
    customer_key, customer_cert = generate_customer_certificate(ca_key, ca_cert, customer_info, cert_dir)
    
    print("\nGenerated files:")
    for file in os.listdir(cert_dir):
        print(f"- certificates/{file}")
    
    print("\nFiles to ship to customer:")
    print("- customer_public_cert.pem (Customer's public certificate)")
    print("- customer_private_key.pem (Customer's private key)")
    print("- license.lic (Will be generated separately)") 