# Kaptifi Vision Marshal - Customer Deployment

## Overview

This is the **customer deployment** version of Kaptifi Vision Marshal - a license validation system for on-premise software deployments. This repository contains **only validation logic** and **no certificate or license generation capabilities** for security reasons.

## 🔒 Security Notice

**Certificate and License Generation Removed**

For security reasons, this customer deployment does **NOT** include:
- ❌ Certificate generation capabilities
- ❌ License generation capabilities  
- ❌ Private key management
- ❌ CA setup tools

All certificate and license generation is performed exclusively at **Kaptifi Marshal HQ**.

## 🎯 What This Repository Contains

### ✅ Included (Customer Deployment)
- License validation engine
- Certificate verification logic
- API endpoints for license status
- Health check endpoints
- Dockerized deployment
- Environment-based configuration

### ❌ Not Included (HQ Only)
- Certificate generation
- License signing
- Private key operations
- CA management tools

## 📁 File Structure

```
kaptifi-vision-marshal/
├── api/                          # API endpoints
│   ├── main.py                   # FastAPI application
│   └── endpoints.py              # License validation endpoints
├── license/                      # License validation logic
│   └── license_validator.py     # Core validation engine
├── helper/                       # Utility functions
│   └── logger.py                 # Logging configuration
├── certificates_data/            # Customer license files
│   ├── license.lic              # License file
│   └── org_cert_public.pem      # Organization certificate
├── logs_data/                    # Application logs
├── docker-compose.yml            # Docker deployment
├── Dockerfile                    # Container configuration
├── requirements.txt              # Python dependencies
└── .env                         # Environment configuration
```

## 🚀 Quick Start

### 1. Environment Setup

Copy the environment template:
```bash
cp env_template .env
```

Configure your license files in `.env`:
```bash
# License Configuration
LICENSE_FILE=./certificates_data/license.lic
ORG_CERT_FILE=./certificates_data/org_cert_public.pem
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Deploy License Files

Place the files received from Kaptifi Marshal HQ:
- `license.lic` - Your organization's license file
- `org_cert_public.pem` - Your organization's certificate

### 4. Start the Service

**Using Docker (Recommended):**
```bash
docker-compose up -d
```

**Using Python directly:**
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### Health Check
```
GET /
```
Returns basic service status.

### License Status
```
GET /api/v1/license
```
Returns detailed license validation information:

```json
{
    "valid": true,
    "message": "License valid",
    "organization_id": "your-org-id",
    "modules": ["counting", "demographics"],
    "issued_on": "2024-01-01",
    "expiration": "2025-12-31"
}
```

## 🔍 License Validation Process

The system performs comprehensive validation:

### 1. Certificate Validation
- ✅ Certificate format verification
- ✅ Certificate expiration check
- ✅ Organization identity verification

### 2. License Validation  
- ✅ License signature verification
- ✅ License expiration check
- ✅ Organization ID matching
- ✅ Module permissions verification

### 3. Security Checks
- ✅ Cryptographic signature validation
- ✅ Certificate-license binding verification
- ✅ Tamper detection
- ✅ Anti-forgery protection

## 🛡️ Security Features

### Backward Compatibility
The validator supports both:
- **Legacy Format**: License data only signatures (current)
- **Secure Format**: Combined certificate + license signatures (future)

### Anti-Tampering
- Digital signatures prevent license modification
- Certificate binding prevents substitution attacks
- Organization ID verification ensures proper licensing

### Offline Validation
- No external dependencies required
- Self-contained validation process
- Works in air-gapped environments

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
DEBUG_MODE=false
HOST=0.0.0.0
PORT=8000
LOGS_DIR=./logs_data

# License Configuration
LICENSE_FILE=./certificates_data/license.lic
ORG_CERT_FILE=./certificates_data/org_cert_public.pem

# Logging Configuration
LOG_LEVEL=INFO
```

### Docker Configuration

The service runs in a containerized environment with:
- Volume mounts for license files
- Volume mounts for logs
- Environment variable configuration
- Health check endpoints

## 📊 Monitoring & Logs

### Log Files
- `logs_data/info.log` - General application logs
- `logs_data/error.log` - Error and warning logs

### Health Monitoring
- Service status: `GET /`
- License status: `GET /api/v1/license`

## 🚨 Troubleshooting

### Common Issues

**License Validation Failed**
```bash
# Check license file exists
ls -la certificates_data/license.lic

# Check certificate file exists  
ls -la certificates_data/org_cert_public.pem

# Check file permissions
chmod 644 certificates_data/*
```

**Certificate Not Found**
- Ensure both `license.lic` and `org_cert_public.pem` are present
- Verify file paths in `.env` configuration
- Check file permissions

**Signature Verification Failed**
- Verify certificate matches the license
- Check for file corruption
- Ensure files are from the same license package

**License Expired**
- Contact Kaptifi Marshal HQ for license renewal
- Check system date/time accuracy

### Getting Help

For support:
1. Check application logs in `logs_data/`
2. Verify license status via API endpoint
3. Contact Kaptifi Marshal HQ for license issues

## 📞 Support

For license generation, renewal, or technical support:
- 📧 Contact: Kaptifi Marshal HQ
- 🌐 License Management: Use Marshal HQ Django application
- 🔧 Technical Issues: Check logs and API endpoints

## 🔄 License Renewal

When your license approaches expiration:
1. Contact Kaptifi Marshal HQ
2. Receive new license files
3. Replace existing files in `certificates_data/`
4. Restart the service
5. Verify new license via API

## ⚠️ Important Security Notes

- **Never attempt to generate certificates locally**
- **Keep certificate files secure and backed up**
- **Monitor license expiration dates**
- **Report any validation issues immediately**
- **Only use license files from official Kaptifi Marshal HQ**

---

**This deployment contains only validation capabilities. All certificate and license generation is performed exclusively at Kaptifi Marshal HQ for maximum security.**