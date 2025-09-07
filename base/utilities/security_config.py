"""
Security Configuration for Central Quality Hub Framework

This module provides security configuration management and setup utilities.
"""

import os
import json
from typing import Dict, Any, List
from base.utilities.security_utils import (
    SecurityManager, CredentialType, SecurityLevel,
    get_security_manager, register_security_user
)


class SecurityConfig:
    """Security configuration management"""
    
    DEFAULT_CONFIG = {
        'master_password': None,  # Will use environment variable
        'max_audit_events': 10000,
        'credential_rotation_interval': 86400,  # 24 hours
        'session_timeout': 3600,  # 1 hour
        'max_failed_attempts': 5,
        'lockout_duration': 300,  # 5 minutes
        'encryption_algorithm': 'AES-256',
        'hash_algorithm': 'SHA-256',
        'compliance_level': 'high',
        'enable_audit_logging': True,
        'audit_log_retention': 2592000,  # 30 days
        'security_alerts': {
            'enable_email_alerts': False,
            'enable_sms_alerts': False,
            'alert_recipients': []
        },
        'vaults': {
            'hashicorp': {
                'enabled': False,
                'url': None,
                'token': None,
                'mount_point': 'secret'
            },
            'aws': {
                'enabled': False,
                'region': 'us-east-1',
                'access_key_id': None,
                'secret_access_key': None
            },
            'azure': {
                'enabled': False,
                'vault_url': None,
                'tenant_id': None,
                'client_id': None,
                'client_secret': None
            }
        },
        'compliance': {
            'gdpr_enabled': True,
            'hipaa_enabled': False,
            'pci_dss_enabled': False,
            'data_retention_days': 90,
            'auto_encrypt_pii': True,
            'mask_sensitive_logs': True
        },
        'access_control': {
            'default_roles': ['user'],
            'admin_roles': ['admin', 'security_admin'],
            'service_roles': ['service', 'automation']
        }
    }
    
    @classmethod
    def load_config(cls, config_file: str = None) -> Dict[str, Any]:
        """Load security configuration from file or environment"""
        config = cls.DEFAULT_CONFIG.copy()
        
        # Load from file if specified
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                print(f"Warning: Failed to load config file {config_file}: {e}")
        
        # Override with environment variables
        config = cls._load_from_environment(config)
        
        return config
    
    @classmethod
    def _load_from_environment(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load configuration overrides from environment variables"""
        env_mappings = {
            'SECURITY_MASTER_PASSWORD': 'master_password',
            'SECURITY_MAX_AUDIT_EVENTS': ('max_audit_events', int),
            'SECURITY_ROTATION_INTERVAL': ('credential_rotation_interval', int),
            'SECURITY_SESSION_TIMEOUT': ('session_timeout', int),
            'SECURITY_COMPLIANCE_LEVEL': 'compliance_level',
            'HASHICORP_VAULT_URL': ('vaults.hashicorp.url', str),
            'HASHICORP_VAULT_TOKEN': ('vaults.hashicorp.token', str),
            'AWS_SECRETS_REGION': ('vaults.aws.region', str),
            'AWS_ACCESS_KEY_ID': ('vaults.aws.access_key_id', str),
            'AWS_SECRET_ACCESS_KEY': ('vaults.aws.secret_access_key', str),
            'AZURE_VAULT_URL': ('vaults.azure.vault_url', str),
            'AZURE_TENANT_ID': ('vaults.azure.tenant_id', str),
            'AZURE_CLIENT_ID': ('vaults.azure.client_id', str),
            'AZURE_CLIENT_SECRET': ('vaults.azure.client_secret', str)
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value:
                if isinstance(config_path, tuple):
                    path, converter = config_path
                    try:
                        env_value = converter(env_value)
                    except ValueError:
                        continue
                else:
                    path = config_path
                
                # Set nested configuration value
                cls._set_nested_config(config, path, env_value)
        
        return config
    
    @classmethod
    def _set_nested_config(cls, config: Dict[str, Any], path: str, value: Any):
        """Set nested configuration value using dot notation"""
        keys = path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    @classmethod
    def save_config(cls, config: Dict[str, Any], config_file: str):
        """Save configuration to file"""
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config to {config_file}: {e}")
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> List[str]:
        """Validate security configuration"""
        issues = []
        
        # Check required fields
        if not config.get('master_password'):
            issues.append("Master password not configured")
        
        # Check vault configurations
        vaults = config.get('vaults', {})
        for vault_name, vault_config in vaults.items():
            if vault_config.get('enabled', False):
                if vault_name == 'hashicorp':
                    if not vault_config.get('url') or not vault_config.get('token'):
                        issues.append(f"HashiCorp Vault enabled but missing URL or token")
                elif vault_name == 'aws':
                    if not vault_config.get('access_key_id') or not vault_config.get('secret_access_key'):
                        issues.append(f"AWS Secrets Manager enabled but missing credentials")
                elif vault_name == 'azure':
                    required_fields = ['vault_url', 'tenant_id', 'client_id', 'client_secret']
                    missing = [f for f in required_fields if not vault_config.get(f)]
                    if missing:
                        issues.append(f"Azure Key Vault enabled but missing: {', '.join(missing)}")
        
        # Check compliance settings
        compliance = config.get('compliance', {})
        if compliance.get('data_retention_days', 0) < 1:
            issues.append("Data retention days must be at least 1")
        
        return issues


def setup_security_framework(config_file: str = None) -> SecurityManager:
    """Setup and initialize the security framework"""
    # Load configuration
    config = SecurityConfig.load_config(config_file)
    
    # Validate configuration
    issues = SecurityConfig.validate_config(config)
    if issues:
        print("Security configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")
        print("Proceeding with default values for missing configurations...")
    
    # Initialize security manager
    security_manager = get_security_manager(config)
    
    # Setup default roles
    access_controller = security_manager.access_controller
    
    # Define standard roles
    access_controller.define_role('admin', [
        'credential:read', 'credential:write', 'credential:delete', 'credential:rotate',
        'user:create', 'user:delete', 'user:modify',
        'audit:read', 'audit:export',
        'system:configure'
    ])
    
    access_controller.define_role('security_admin', [
        'credential:read', 'credential:write', 'credential:delete', 'credential:rotate',
        'audit:read', 'audit:export',
        'security:configure'
    ])
    
    access_controller.define_role('user', [
        'credential:read'
    ])
    
    access_controller.define_role('service', [
        'credential:read', 'credential:rotate'
    ])
    
    access_controller.define_role('automation', [
        'credential:read', 'credential:write'
    ])
    
    # Register default users if specified in config
    default_users = config.get('default_users', [])
    for user_config in default_users:
        user_id = user_config.get('user_id')
        roles = user_config.get('roles', ['user'])
        if user_id:
            register_security_user(user_id, roles)
    
    print("Security framework initialized successfully")
    return security_manager


def create_test_credentials(security_manager: SecurityManager, user_id: str = 'admin'):
    """Create test credentials for development/testing"""
    test_credentials = [
        {
            'id': 'test_api_key',
            'value': 'sk-test-1234567890abcdef',
            'type': CredentialType.API_KEY,
            'description': 'Test API Key',
            'security_level': SecurityLevel.MEDIUM
        },
        {
            'id': 'test_database_password',
            'value': 'test_db_password_123',
            'type': CredentialType.PASSWORD,
            'description': 'Test Database Password',
            'security_level': SecurityLevel.HIGH
        },
        {
            'id': 'test_jwt_token',
            'value': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test',
            'type': CredentialType.TOKEN,
            'description': 'Test JWT Token',
            'security_level': SecurityLevel.MEDIUM
        },
        {
            'id': 'test_connection_string',
            'value': 'mongodb://testuser:testpass@localhost:27017/testdb',
            'type': CredentialType.CONNECTION_STRING,
            'description': 'Test MongoDB Connection',
            'security_level': SecurityLevel.HIGH
        }
    ]
    
    for cred in test_credentials:
        success = security_manager.store_credential(
            credential_id=cred['id'],
            credential_value=cred['value'],
            credential_type=cred['type'],
            user_id=user_id,
            description=cred['description'],
            security_level=cred['security_level']
        )
        
        if success:
            print(f"Created test credential: {cred['id']}")
        else:
            print(f"Failed to create test credential: {cred['id']}")


def demonstrate_security_features():
    """Demonstrate security framework features"""
    print("\n=== Security Framework Demonstration ===")
    
    # Initialize security framework
    security_manager = setup_security_framework()
    
    # Register test user
    register_security_user('test_user', ['user'])
    register_security_user('test_admin', ['admin'])
    
    # Create test credentials
    create_test_credentials(security_manager, 'test_admin')
    
    # Demonstrate credential retrieval
    print("\n--- Credential Retrieval ---")
    api_key = security_manager.get_credential('test_api_key', 'test_user')
    if api_key:
        print(f"Retrieved API key: {api_key[:10]}...")
    else:
        print("Failed to retrieve API key")
    
    # Demonstrate sensitive data detection
    print("\n--- Sensitive Data Detection ---")
    test_text = "password=secret123 and api_key=sk-1234567890"
    sanitized = security_manager.sanitize_log_message(test_text)
    print(f"Original: {test_text}")
    print(f"Sanitized: {sanitized}")
    
    # Demonstrate compliance checking
    print("\n--- Compliance Checking ---")
    compliance_report = security_manager.check_data_compliance(test_text)
    print(f"Compliance status: {compliance_report}")
    
    # Generate security report
    print("\n--- Security Report ---")
    report = security_manager.generate_security_report()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    demonstrate_security_features()
