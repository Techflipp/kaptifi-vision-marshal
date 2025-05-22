# Kaptifi-Vision-Marshal Feature Roadmap

## Status
- License File Format & Generator Tool: **In Progress**
- License Validator & Monitor (Marshal Core): Pending
- Distributed Watchdog Client: Pending
- Email Notifier & Data Deletion: Pending
- Customer & License Management Web App: Pending

> Status updates are tracked here only. The README will not include status updates.

### Module Checklist
- [x] Project structure modularized (folders created)
- [ ] License Generator
- [ ] Marshal Core (Validator & Monitor)
- [ ] Distributed Watchdog Client
- [ ] Email Notifier & Data Deletion
- [ ] Customer & License Management Web App

## Overview
Kaptifi-Vision-Marshal is a simple license controller for on-premise deployments of the Kaptifi-Vision project. It manages access to modules like object counting and demographics based on subscription periods.

## Simplified Approach
We'll implement a primarily offline license system with minimal complexity, focusing on reliability and ease of use.

## How It Works: Customer Journey

### 1. License Creation & Deployment
- **When:** Customer purchases a subscription
- **What happens:**
  - You generate a license file with expiration date and enabled modules
  - License file is encrypted with a private key only you possess
  - Customer receives the license file to deploy with their system
  - The license file contains: customer ID, expiration date, enabled modules, and customer email

### 2. System Installation
- Customer installs Kaptifi-Vision with the Marshal component
- During installation, they provide the license file
- Marshal validates the license file using a built-in public key
- If valid, system activates and stores the license locally

### 3. Daily Operation & Monitoring
- Marshal continuously monitors running containers (not just on restarts)
- Marshal checks the license file at regular intervals
- If license is valid, containers operate normally
- If expired, containers are stopped and a grace period begins
- Email reminders are sent to the customer before expiry and during the grace period

### 4. Grace Period & Data Deletion
- System enters a 7-day grace period after license expiry
- During grace period, email reminders are sent
- If license is not renewed within 7 days, Marshal securely deletes all related data:
  - Local files
  - Database
  - Docker registry
  - Everything in the deployment folder related to Kaptifi-Vision

### 5. License Renewal & Offline Update
- **Option 1: Fully Offline Renewal**
  - Customer contacts you when renewal is needed
  - You generate a new license file with extended expiration
  - Customer replaces the old license file manually (offline update)
  
- **Option 2: Simple Online Renewal** (optional)
  - Customer clicks "Renew License" in admin interface
  - System connects to your license server (if internet available)
  - New license is downloaded and installed automatically

### 6. Distributed License Watchdog (Anti-Bypass)
- Marshal exposes license status and heartbeat (via local API or signed status file in shared volume)
- Each module container (e.g., counting, demographics) includes a watchdog client
- Module containers check Marshal's status at intervals (e.g., every minute)
- If Marshal is removed, unreachable, or license is invalid, modules stop themselves
- Status communication is cryptographically protected to prevent spoofing

## Core Components

### 1. License Generator (Your Tool)
- Simple command-line or web tool you use internally
- Inputs: customer ID, subscription end date, enabled modules, customer email
- Output: encrypted license file for customer

### 2. License Validator & Monitor (Part of Marshal)
- Built into the Marshal component
- Reads and validates license file using public key
- Checks system date against expiration date
- Continuously monitors containers and license validity
- Controls container startup and running state based on validity
- Triggers data deletion after grace period

### 3. Email Notifier
- Stores customer email from config/license
- Sends automated reminders before expiry and during grace period

### 4. Container Control
- Simple integration with Docker/Kubernetes
- Prevents container startup and stops running containers when license is invalid
- Provides clear error messages about license status

### 5. Data Deletion Module
- Securely deletes all related data after grace period if license is not renewed

### 6. Distributed Watchdog Client
- Lightweight client in each module container
- Checks Marshal's status/heartbeat at intervals
- Stops module container if Marshal is missing or license is invalid

### 7. Customer & License Management Web App
- Simple web application (e.g., Django)
- UI to manage customer list and generate license files
- Central place for license creation, renewal, and customer management

## Security Considerations (Simplified)
- Use standard encryption (RSA or similar) for license files
- Include basic hardware identifier to prevent license copying
- Implement simple system date validation to detect clock manipulation
- Secure deletion of sensitive data after grace period
- Cryptographically protect status/heartbeat communication

## Implementation Timeline
1. **Week 1-2:** Develop license file format and generator tool (with email field)
2. **Week 3-4:** Implement license validator, container monitor, and email notifier in Marshal
3. **Week 5-6:** Integrate with container startup/running process, data deletion module, and distributed watchdog client
4. **Week 7-8:** Develop simple web app for customer/license management
5. **Week 9:** Testing and refinement

## Benefits of This Approach
- Works completely offline after initial deployment
- Simple to understand and maintain
- Minimal points of failure
- Easy for customers to manage
- No complex online verification systems to build
- Automated reminders and secure data handling for compliance
- Tamper-resistant and robust against bypass attempts 