# Kaptifi Vision License Management - Detailed Guide

## Journey Overview

```mermaid
journey
    title License Management Journey
    section 1. Initial Setup (One-time)
        Generate CA certificates: 5: Company
        Store CA private key: 5: Company
        Distribute CA public cert: 3: Company
    section 2. Customer Onboarding
        Create customer certificate: 5: Company
        Generate customer keys: 5: Company
        Deliver to customer: 3: Company, Customer
    section 3. License Creation
        Receive certificate & keys: 5: Customer
        Define permissions & dates: 5: Customer
        Create signed license: 3: Customer
    section 4. Runtime Validation
        Load certificates: 5: System
        Verify certificate chain: 5: System
        Validate license: 5: System
        Enable features: 3: System
```

## Detailed Process Breakdown

### 1. Initial Setup (One-time Company Setup)

**Files Created:**
- `ca_private_key.pem`: 
  - 4096-bit RSA private key
  - Used to sign all customer certificates
  - MUST be kept secure and backed up
  - Never shared with anyone

- `ca_cert_public.pem`:
  - Public certificate containing CA's identity
  - Used to verify customer certificates
  - Embedded in the application
  - Valid for 10 years

**Technical Process:**
```bash
# Generate CA certificate
python license/ca_setup.py

# Verification
openssl x509 -in certificates/ca_cert_public.pem -text -noout
```

### 2. Customer Onboarding

**Files Generated:**
- `customer_public_cert.pem`:
  - Contains customer's identity
  - Signed by CA private key
  - Valid for 1 year
  - Includes:
    - Organization name
    - Country (SA)
    - License ID
    - Public key

- `customer_private_key.pem`:
  - 2048-bit RSA private key
  - Used to sign license files
  - Must be protected by customer
  - Never transmitted over network

**Technical Process:**
```python
customer_info = {
    "company": "Customer Company",
    "country": "SA",
    "organization_id": "611bac12-becd-45fa-b55d-e233650f4d54"
}
```

**Validation Checks:**
- Certificate chain verification
- Expiration date check
- Organization name validation
- Digital signature verification

### 3. License Creation

**License File Structure (`license.lic`):**
```json
{
    "certificate": "BASE64_ENCODED_CUSTOMER_CERT",
    "license": {
        "organization_id": "611bac12-becd-45fa-b55d-e233650f4d54",
        "modules": [
            "counting",
            "demographics"
        ],
        "issued_on": "2024-01-01",
        "expiration": "2025-12-31"
    },
    "signature": "DIGITAL_SIGNATURE_HEX"
}
```

**Technical Details:**
- Certificate encoding: Base64
- Signature algorithm: SHA-256 with PSS padding
- Key format: PKCS#8
- File format: JSON

**Generation Process:**
1. Load customer certificate
2. Create license data
3. Sign with customer's private key
4. Package all components
5. Save as license.lic

### 4. Runtime Validation

**Validation Steps:**
1. **Certificate Chain Verification:**
   - Load CA public certificate
   - Verify customer certificate signature
   - Check certificate dates
   - Validate customer details

2. **License Validation:**
   - Decode customer certificate
   - Verify license signature
   - Check expiration dates
   - Validate organization ID match
   - Confirm module permissions

3. **Security Checks:**
   - Certificate integrity
   - Signature authenticity
   - Time validity
   - Permission scope

**Error Handling:**
- Certificate expired
- Invalid signature
- Tampered license
- Missing modules
- Invalid organization ID

## Security Considerations

### Private Key Protection
- CA private key:
  - Stored offline
  - Access-controlled
  - Encrypted storage
  - Regular backup

### Customer Key Management
- Secure delivery process
- Installation verification
- Backup recommendations
- Update procedures

### License Security
- Tamper-evident design
- Digital signatures
- Time-based validation
- Module-level control

## File Locations
certificates/
├── ca_cert_public.pem # CA's public certificate
├── ca_private_key.pem # CA's private key (secured)
├── customer_public_cert.pem # Customer's certificate
├── customer_private_key.pem # Customer's private key
└── license.lic # Active license file


## API Integration

**Endpoints:**
- `GET /api/v1/license`: Check license status
- Response includes:
  - Validation status
  - Certificate details
  - Module permissions
  - Expiration dates

**Example Response:**
```json
{
    "valid": true,
    "message": "License valid",
    "organization_id": "611bac12-becd-45fa-b55d-e233650f4d54",
    "modules": ["counting", "demographics"],
    "issued_on": "2024-01-01",
    "expiration": "2025-12-31"
}
```

## Troubleshooting Guide

### Common Issues:
1. **Certificate Errors:**
   - Expired certificate
   - Invalid signature
   - Chain verification failed

2. **License Errors:**
   - Expired license
   - Invalid modules
   - Signature mismatch

3. **System Issues:**
   - File permissions
   - Missing certificates
   - Invalid file format

### Resolution Steps:
1. Verify file locations
2. Check file permissions
3. Validate dates
4. Confirm signatures
5. Review logs

## Maintenance Procedures

### Regular Tasks:
1. Certificate renewal
2. License updates
3. Security audits
4. Backup verification
