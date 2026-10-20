# Hound Security Guide

This document covers security considerations for Hound.

## Overview

Hound is designed as a LAN-only household dashboard with the following security principles:

- **Defense in Depth**: Multiple layers of security
- **Least Privilege**: Minimal access required
- **Secure Defaults**: No default passwords
- **Transparent Security**: Security is visible and auditable
- **Local-First**: Data stays on the device

## Threat Model

Hound protects against:

- Unauthorized access to management interface
- Data theft from device compromise
- Malicious file uploads
- SQL injection
- XSS attacks
- CSRF attacks
- Brute-force authentication
- Privilege escalation

Hound does NOT protect against:

- Physical device theft (use full-disk encryption)
- Compromised home network
- Zero-day vulnerabilities in dependencies
- Side-channel attacks
- Physical access to device (use secure bootloader, etc.)

## Authentication

### Password/ PIN

- **Storage**: Hashed with bcrypt
- **Algorithm**: bcrypt with cost factor 12
- **No Defaults**: User must create credential on first setup
- **Change Flow**: Secure credential change endpoint
- **Throttling**: 5 failed attempts = 15-minute lockout
- **Token-based**: JWT access tokens (24-hour expiry)

### JWT Tokens

- **Algorithm**: HS256
- **Secret**: Configured via `HOUND_SECRET_KEY`
- **Expiry**: 24 hours
- **Storage**: localStorage (browser)
- **Transmission**: Authorization header

### Recommendations

1. Use a strong password (12+ characters, mixed case, numbers, symbols)
2. Change the secret key in `.env` to a unique value
3. Don't share the management URL outside your home network
4. Consider using a longer password instead of a short PIN

## Network Security

### LAN-Only Binding

By default, Hound binds to all interfaces but should be accessed only from LAN.

**Recommended Configuration**:

```yaml
# docker-compose.yml
frontend:
  ports:
    - "192.168.1.100:3000:80"  # Replace with your LAN IP
```

### Firewall

Configure UFW to restrict access:

```bash
# Default deny incoming
sudo ufw default deny incoming

# Allow outgoing
sudo ufw default allow outgoing

# Allow from home network only
sudo ufw allow from 192.168.1.0/24 to any port 3000

# Enable
sudo ufw enable
```

### No Public Exposure

**Do NOT**:
- Configure router port forwarding
- Expose services to public internet
- Use dynamic DNS for public access
- Enable remote management tools

**If public access is absolutely required** (not recommended):
- Set up a VPN (WireGuard, OpenVPN)
- Use reverse proxy with HTTPS
- Implement rate limiting
- Add fail2ban
- Use strong authentication (MFA if possible)

## Application Security

### Input Validation

All input is validated on the backend using Pydantic schemas:

- Type checking
- Length limits
- Format validation
- Range validation
- Custom validators

### SQL Injection Prevention

- Parameterized queries via SQLAlchemy
- No raw SQL concatenation
- ORM-based queries

### XSS Prevention

- React automatically escapes content
- No `dangerouslySetInnerHTML` without sanitization
- Content Security Policy (CSP) recommended

### CSRF Protection

- Same-origin policy enforced
- JWT tokens in Authorization header (not cookies)
- No cookie-based authentication

### File Upload Security

File uploads are validated:

- **Allowed types**: JPEG, PNG, GIF, WebP only
- **Size limit**: 10MB maximum
- **Content verification**: Magic number verification
- **Safe filenames**: UUID-based, no user control
- **Path traversal prevention**: No path from user input
- **No execution**: Uploaded files never executed

### Secrets Management

**Never commit secrets to git**:
- `.env` is in `.gitignore`
- Use `.env.example` as template
- Document required variables

**Secret storage**:
- Database passwords: Environment variables
- JWT secret: Environment variables
- API keys: Environment variables (none currently used)

## Data Security

### Encryption at Rest

**Current**: No encryption at rest (future enhancement)

**Recommendations**:
- Enable full-disk encryption on the device
- Use LUKS on Linux
- Encrypt backups if copying off-device

### Data in Transit

**Current**: HTTP (no TLS)

**Recommendations**:
- Set up reverse proxy with HTTPS (nginx + Let's Encrypt)
- Use strong TLS configuration
- Enable HSTS

### Database Security

- SQLite file in Docker volume
- WAL mode enabled
- Foreign key constraints
- No SQL injection risk
- Regular backups

### Photo Storage

- UUID-based filenames
- No directory traversal
- Safe storage location
- No metadata exposure

## Dependency Security

### Keeping Dependencies Updated

```bash
# Backend
cd backend
pip list --outdated
pip install --upgrade <package>

# Frontend
cd frontend
npm outdated
npm update
```

### Vulnerability Scanning

```bash
# Backend
pip-audit

# Frontend
npm audit
npm audit fix
```

### Pinned Versions

- Backend: Version ranges in pyproject.toml
- Frontend: package-lock.json
- Docker: Specific base image tags

## Operational Security

### Updates

- Automatic updates with health checks
- Pre-update backup
- Rollback capability
- Update channel selection (stable/beta)

### Backups

- Automatic scheduled backups
- Manual backup capability
- Off-device backup recommended
- Backup integrity verification

### Logging

- Structured logging
- No sensitive data in logs
- No passwords or tokens in logs
- Log rotation (Docker)

### Monitoring

- Health check endpoints
- System status tracking
- Component-level status
- Error tracking

## Physical Security

### Device Security

- Secure location (central household location)
- Physical access control
- Consider Kensington lock
- Full-disk encryption
- Secure boot (if supported)

### Kiosk Mode

- Full-screen browser
- No desktop access
- No keyboard shortcuts
- Automatic restart on crash

## User Security

### Access Control

- Single household credential
- No user accounts (simpler model)
- LAN-only access
- No remote access

### Privacy

- No cloud accounts
- No third-party tracking
- No analytics
- No data sharing
- Local-only data storage

## Compliance and Best Practices

### OWASP Top 10

Hound addresses:
- **A01: Broken Access Control**: Authenticated management interface
- **A02: Cryptographic Failures**: Password hashing, no hardcoded secrets
- **A03: Injection**: Parameterized queries, input validation
- **A04: Insecure Design**: Local-first, minimal attack surface
- **A05: Security Misconfiguration**: Secure defaults, documentation
- **A06: Vulnerable Components**: Dependency updates, scanning
- **A07: Authentication Failures**: Bcrypt, throttling, JWT
- **A08: Software/Data Integrity**: Backup verification, signed updates
- **A09: Logging Failures**: Structured logging, no sensitive data
- **A10: SSRF**: No external requests from user input

### Security Checklist

- [ ] Set strong management password
- [ ] Change `HOUND_SECRET_KEY` in `.env`
- [ ] Configure firewall rules
- [ ] Enable full-disk encryption
- [ ] Set up off-device backups
- [ ] Configure HTTPS (optional but recommended)
- [ ] Regular dependency updates
- [ ] Monitor system status
- [ ] Review logs periodically
- [ ] Test restore procedure

## Incident Response

### Suspected Compromise

1. **Immediate Actions**:
   - Disconnect device from network
   - Do not power off (preserves evidence)
   - Change management password
   - Review system status

2. **Investigation**:
   - Check logs for suspicious activity
   - Review backup integrity
   - Check for unknown files
   - Verify configuration

3. **Recovery**:
   - Restore from known-good backup
   - Change all credentials
   - Update dependencies
   - Reconfigure security settings
   - Monitor for recurrence

### Data Breach

If household data is exposed:

1. Identify what was exposed
2. Assess risk (photos, events, settings)
3. Notify household members
4. Change credentials
5. Review security practices
6. Document the incident

## Security Hardening

### Optional Enhancements

1. **HTTPS**:
   - Set up nginx reverse proxy
   - Use Let's Encrypt certificates
   - Enable HSTS

2. **Fail2Ban**:
   - Install fail2ban
   - Configure for HTTP auth failures
   - Block repeated failures

3. **AppArmor**:
   - Create profile for containers
   - Restrict file system access
   - Limit network access

4. **VPN**:
   - Set up WireGuard
   - Require VPN for remote access
   - Multi-factor authentication

5. **Audit Logging**:
   - Log all management actions
   - Log authentication attempts
   - Regular log review

## Limitations

### What Hound Does NOT Protect Against

- Physical device theft (use encryption)
- Compromised home network
- Zero-day vulnerabilities
- Nation-state actors
- Side-channel attacks
- Physical tampering

### Known Limitations

- HTTP by default (no TLS)
- No multi-factor authentication
- No audit logging
- No intrusion detection
- No file encryption at rest
- Single credential model

## Reporting Security Issues

If you discover a security vulnerability:

1. Do NOT create a public issue
2. Email security contact (to be configured)
3. Provide details and reproduction steps
4. Allow time for fix before disclosure
5. Follow responsible disclosure

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [React Security](https://react.dev/learn/keeping-components-pure)
