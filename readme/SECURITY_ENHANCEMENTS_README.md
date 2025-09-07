# Security Enhancements - Central Quality Hub Framework

## Overview

The Security Enhancements module provides comprehensive security capabilities for the Central Quality Hub automation framework, including secure credential management, data protection, access control, and vault integrations.

## Features

### 🔐 Credential Management
- **Secure Storage**: AES-256 encrypted credential storage with PBKDF2 key derivation
- **Access Control**: Role-based access control with granular permissions  
- **Credential Rotation**: Automated and manual credential rotation capabilities
- **Multiple Types**: Support for passwords, API keys, tokens, certificates, connection strings, and SSH keys
- **Audit Trail**: Complete audit logging of all credential operations

### 🛡️ Sensitive Data Protection
- **Pattern Detection**: Advanced regex-based detection of sensitive data patterns
- **Data Sanitization**: Automatic sanitization of logs and data transmissions
- **Data Masking**: Configurable data masking with partial visibility
- **Compliance Checking**: GDPR, HIPAA, and PCI-DSS compliance validation
- **Custom Patterns**: Support for custom sensitive data patterns

### 🔒 Security Best Practices
- **Encryption at Rest**: All stored credentials encrypted with industry-standard algorithms
- **Secure Communication**: TLS/SSL enforcement for all external communications
- **Session Management**: Secure session handling with timeout and invalidation
- **Security Headers**: Automatic security header injection
- **Input Validation**: Comprehensive input validation and sanitization

### 🏛️ Vault Integration
- **HashiCorp Vault**: Native integration with HashiCorp Vault
- **AWS Secrets Manager**: AWS Secrets Manager integration
- **Azure Key Vault**: Azure Key Vault integration
- **Multi-Vault**: Support for multiple vault backends simultaneously
- **Failover**: Automatic failover between vault providers

## Architecture

```
Security Framework
├── SecurityManager (Main orchestrator)
├── EncryptionManager (Encryption/decryption)
├── AccessController (Role-based access control)
├── SecureCredentialStore (Credential storage)
├── SensitiveDataDetector (Data protection)
├── SecurityAuditor (Audit trail)
├── VaultIntegrations (External vault backends)
└── SecureConfigurationLoader (Secure config loading)
```

## Quick Start

### Basic Setup

```python
from base.utilities.security_utils import get_security_manager, register_security_user
from base.utilities.security_config import setup_security_framework

# Initialize security framework
security_manager = setup_security_framework()

# Register users
register_security_user('admin_user', ['admin'])
register_security_user('test_user', ['user'])
```

### Credential Management

```python
from base.utilities.security_utils import (
    store_secure_credential, get_secure_credential, CredentialType
)

# Store credential
success = store_secure_credential(
    credential_id='api_key_prod',
    value='sk-1234567890abcdef',
    credential_type=CredentialType.API_KEY,
    user_id='admin_user'
)

# Retrieve credential
api_key = get_secure_credential('api_key_prod', 'admin_user')
```

### Sensitive Data Protection

```python
from base.utilities.security_utils import sanitize_sensitive_data, check_security_compliance

# Sanitize sensitive data in logs
log_message = "User login with password=secret123"
safe_message = sanitize_sensitive_data(log_message)
# Result: "User login with ***REDACTED***"

# Check compliance
data = "Email: user@example.com, Password: secret123"
compliance_report = check_security_compliance(data)
print(compliance_report['compliant'])  # False
print(compliance_report['findings'])   # {'email': [...], 'password': [...]}
```

## Configuration

### Environment Variables

```bash
# Master encryption password
SECURITY_MASTER_PASSWORD=your_secure_master_password

# Audit settings
SECURITY_MAX_AUDIT_EVENTS=10000
SECURITY_ROTATION_INTERVAL=86400

# HashiCorp Vault
HASHICORP_VAULT_URL=http://localhost:8200
HASHICORP_VAULT_TOKEN=your_vault_token

# AWS Secrets Manager
AWS_SECRETS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Azure Key Vault
AZURE_VAULT_URL=https://your-vault.vault.azure.net/
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
```

### Configuration File

```json
{
  "master_password": "secure_master_password",
  "max_audit_events": 10000,
  "credential_rotation_interval": 86400,
  "compliance": {
    "gdpr_enabled": true,
    "hipaa_enabled": false,
    "auto_encrypt_pii": true,
    "mask_sensitive_logs": true
  },
  "vaults": {
    "hashicorp": {
      "enabled": true,
      "url": "http://localhost:8200",
      "token": "vault_token"
    },
    "aws": {
      "enabled": true,
      "region": "us-east-1"
    }
  }
}
```

## API Reference

### SecurityManager

Main security orchestrator providing unified access to all security features.

#### Methods

```python
# User management
register_user(user_id: str, roles: List[str] = None)

# Credential operations
store_credential(credential_id: str, credential_value: str, 
                credential_type: CredentialType, user_id: str, **kwargs) -> bool
get_credential(credential_id: str, user_id: str) -> Optional[str]

# Data protection
sanitize_log_message(message: str) -> str
check_data_compliance(data: str) -> Dict[str, Any]

# Reporting
generate_security_report() -> Dict[str, Any]

# Secure operations
@contextmanager
secure_operation(user_id: str, operation: str, resource: str)
```

### EncryptionManager

Handles all encryption and decryption operations.

#### Methods

```python
encrypt(data: str) -> str
decrypt(encrypted_data: str) -> str
hash_password(password: str, salt: str = None) -> Dict[str, str]
verify_password(password: str, password_hash: str, salt: str) -> bool
generate_key() -> str
```

### AccessController

Manages role-based access control.

#### Methods

```python
define_role(role_name: str, permissions: List[str])
assign_role(user_id: str, role_name: str)
check_permission(user_id: str, permission: str) -> bool
revoke_role(user_id: str, role_name: str)
get_user_permissions(user_id: str) -> Set[str]
```

### SensitiveDataDetector

Detects and protects sensitive data.

#### Methods

```python
detect_sensitive_data(text: str) -> Dict[str, List[str]]
sanitize_text(text: str, replacement: str = "***REDACTED***") -> str
mask_data(text: str, show_chars: int = 3) -> str
add_custom_pattern(category: str, pattern: str)
```

### SecurityAuditor

Provides security audit trail and monitoring.

#### Methods

```python
log_event(event_type: str, user_id: str, resource: str, 
         action: str, success: bool, **kwargs) -> str
get_events(event_type: str = None, user_id: str = None, 
          start_time: datetime = None, end_time: datetime = None) -> List[SecurityAuditEvent]
get_failed_attempts(time_window: int = 3600) -> List[SecurityAuditEvent]
export_audit_log(filepath: str, format: str = 'json')
```

## Vault Integrations

### HashiCorp Vault

```python
from base.utilities.security_utils import HashiCorpVaultIntegration

vault = HashiCorpVaultIntegration(
    vault_url='http://localhost:8200',
    vault_token='your_token',
    mount_point='secret'
)

# Store secret
vault.store_secret('my_secret', 'secret_value')

# Retrieve secret
secret = vault.retrieve_secret('my_secret')
```

### AWS Secrets Manager

```python
from base.utilities.security_utils import AWSSecretsManagerIntegration

vault = AWSSecretsManagerIntegration(
    region_name='us-east-1',
    aws_access_key_id='your_key',
    aws_secret_access_key='your_secret'
)
```

### Azure Key Vault

```python
from base.utilities.security_utils import AzureKeyVaultIntegration

vault = AzureKeyVaultIntegration(
    vault_url='https://your-vault.vault.azure.net/'
)
```

## Security Best Practices

### 1. Credential Management
- Always use the highest security level appropriate for your credentials
- Implement regular credential rotation
- Use strong, unique passwords for encryption keys
- Limit credential access to minimum required permissions

### 2. Data Protection
- Enable sensitive data detection for all logs and transmissions
- Use data masking in non-production environments
- Implement compliance checking for regulatory requirements
- Regularly audit data access patterns

### 3. Access Control
- Follow principle of least privilege
- Use role-based access control consistently
- Regularly review and audit user permissions
- Implement session timeouts and secure session management

### 4. Monitoring and Auditing
- Enable comprehensive audit logging
- Monitor for suspicious access patterns
- Set up alerts for security events
- Regularly export and archive audit logs

### 5. Vault Usage
- Use external vaults for production credentials
- Implement vault failover strategies
- Regularly backup vault configurations
- Monitor vault performance and availability

## Testing

### Running Security Tests

```bash
# Run all security tests
python test_security_utils.py

# Run with pytest
pytest test_security_utils.py -v

# Run specific test categories
pytest test_security_utils.py::TestEncryptionManager -v
pytest test_security_utils.py::TestAccessController -v
```

### Test Coverage

The security framework includes comprehensive tests for:
- ✅ Encryption and decryption
- ✅ Password hashing and verification
- ✅ Access control and permissions
- ✅ Credential storage and retrieval
- ✅ Sensitive data detection
- ✅ Security auditing
- ✅ Vault integrations
- ✅ Configuration management
- ✅ Integration workflows

## Compliance

### GDPR Compliance
- Automatic PII detection and protection
- Data subject rights implementation
- Data retention policy enforcement
- Consent management integration

### HIPAA Compliance
- PHI data identification and protection
- Access control and audit requirements
- Encryption requirements compliance
- Breach notification support

### PCI-DSS Compliance
- Credit card data detection
- Secure storage requirements
- Access control standards
- Regular security testing

## Troubleshooting

### Common Issues

#### 1. Encryption/Decryption Errors
```python
# Check master password configuration
import os
print(os.environ.get('SECURITY_MASTER_PASSWORD'))

# Verify salt file permissions
import os
print(os.path.exists('.security_salt'))
```

#### 2. Access Denied Errors
```python
# Check user roles and permissions
security_manager = get_security_manager()
permissions = security_manager.access_controller.get_user_permissions('user_id')
print(permissions)
```

#### 3. Vault Connection Issues
```python
# Test vault connectivity
from base.utilities.security_utils import HashiCorpVaultIntegration
vault = HashiCorpVaultIntegration('http://localhost:8200', 'token')
secrets = vault.list_secrets()  # Should not raise exception
```

### Performance Optimization

1. **Credential Caching**: Implement credential caching for frequently accessed secrets
2. **Batch Operations**: Use batch operations for multiple credential retrievals
3. **Async Operations**: Consider async implementations for vault operations
4. **Connection Pooling**: Use connection pooling for vault integrations

### Security Monitoring

Monitor these metrics for security health:
- Failed authentication attempts
- Unusual access patterns
- Credential rotation compliance
- Vault availability and performance
- Compliance violations

## Migration Guide

### From Basic Authentication
```python
# Before: Plain text credentials
username = "admin"
password = "password123"

# After: Secure credential management
security_manager = get_security_manager()
register_security_user('admin', ['admin'])
store_secure_credential('admin_password', 'password123', CredentialType.PASSWORD, 'admin')
password = get_secure_credential('admin_password', 'admin')
```

### From Environment Variables
```python
# Before: Environment variables
api_key = os.environ.get('API_KEY')

# After: Secure storage with vault integration
security_manager = get_security_manager()
# Store once in vault or secure store
store_secure_credential('api_key', api_key, CredentialType.API_KEY, 'admin')
# Retrieve securely
api_key = get_secure_credential('api_key', 'service_user')
```

## Contributing

### Security Guidelines
1. All security-related changes require security review
2. Follow secure coding practices
3. Update tests for any security feature changes
4. Document security implications of changes
5. Use static analysis tools for security scanning

### Adding New Features
1. Create comprehensive tests first
2. Follow existing patterns and architecture
3. Update documentation
4. Consider compliance implications
5. Implement proper audit logging

## License

This security framework is part of the Central Quality Hub project and follows the same licensing terms.

## Support

For security-related questions or issues:
1. Check the troubleshooting section
2. Review the test cases for examples
3. Consult the API reference
4. Create an issue with security implications clearly documented

---

**⚠️ Security Notice**: This framework handles sensitive security operations. Always follow security best practices and keep the framework updated with the latest security patches.
