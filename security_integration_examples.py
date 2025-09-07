"""
Security Integration Examples for Central Quality Hub Framework

This module demonstrates practical integration of security features
into various automation testing scenarios.
"""

import time
import json
from datetime import datetime
from contextlib import contextmanager
from base.utilities.security_utils import (
    get_security_manager, register_security_user, CredentialType, SecurityLevel,
    store_secure_credential, get_secure_credential, sanitize_sensitive_data,
    check_security_compliance, secure_operation_context
)
from base.utilities.security_config import setup_security_framework


class SecureWebTestExample:
    """Example of secure web testing with credential management"""
    
    def __init__(self):
        self.security_manager = get_security_manager()
        register_security_user('web_tester', ['automation', 'user'])
    
    def setup_test_credentials(self):
        """Setup secure credentials for web testing"""
        credentials = [
            {
                'id': 'web_admin_user',
                'value': 'admin@example.com',
                'type': CredentialType.CUSTOM,
                'description': 'Web application admin username'
            },
            {
                'id': 'web_admin_password',
                'value': 'SecureAdminPass123!',
                'type': CredentialType.PASSWORD,
                'description': 'Web application admin password',
                'security_level': SecurityLevel.HIGH
            },
            {
                'id': 'test_api_token',
                'value': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token',
                'type': CredentialType.TOKEN,
                'description': 'API authentication token'
            }
        ]
        
        for cred in credentials:
            store_secure_credential(
                credential_id=cred['id'],
                value=cred['value'],
                credential_type=cred['type'],
                user_id='web_tester'
            )
        
        print("✓ Web test credentials setup complete")
    
    def secure_login_test(self):
        """Example of secure login test with credential protection"""
        with secure_operation_context('web_tester', 'login_test', 'web_application'):
            # Retrieve credentials securely
            username = get_secure_credential('web_admin_user', 'web_tester')
            password = get_secure_credential('web_admin_password', 'web_tester')
            
            if not username or not password:
                raise Exception("Failed to retrieve login credentials")
            
            # Simulate login process (credentials never exposed in logs)
            print(f"Performing login with user: {username}")
            
            # Log sanitized version
            log_message = f"Login attempt for user: {username} with password: {password}"
            safe_log = sanitize_sensitive_data(log_message)
            print(f"Safe log: {safe_log}")
            
            # Simulate successful login
            print("✓ Secure login test completed")
    
    def api_test_with_token(self):
        """Example of API testing with secure token management"""
        with secure_operation_context('web_tester', 'api_test', 'api_endpoint'):
            # Get API token
            token = get_secure_credential('test_api_token', 'web_tester')
            
            if not token:
                raise Exception("Failed to retrieve API token")
            
            # Use token for API call (token protected in logs)
            headers = {'Authorization': f'Bearer {token}'}
            
            # Log safe version
            safe_headers = sanitize_sensitive_data(str(headers))
            print(f"API call with headers: {safe_headers}")
            
            print("✓ Secure API test completed")


class SecureDatabaseTestExample:
    """Example of secure database testing with connection protection"""
    
    def __init__(self):
        self.security_manager = get_security_manager()
        register_security_user('db_tester', ['automation', 'user'])
    
    def setup_database_credentials(self):
        """Setup secure database credentials"""
        db_credentials = [
            {
                'id': 'mysql_connection',
                'value': 'mysql://testuser:SecurePass123@localhost:3306/testdb',
                'type': CredentialType.CONNECTION_STRING,
                'description': 'MySQL test database connection',
                'security_level': SecurityLevel.HIGH
            },
            {
                'id': 'mongodb_connection',
                'value': 'mongodb://admin:MongoPass456@localhost:27017/testdb?authSource=admin',
                'type': CredentialType.CONNECTION_STRING,
                'description': 'MongoDB test database connection',
                'security_level': SecurityLevel.HIGH
            },
            {
                'id': 'redis_password',
                'value': 'RedisSecurePass789',
                'type': CredentialType.PASSWORD,
                'description': 'Redis database password',
                'security_level': SecurityLevel.MEDIUM
            }
        ]
        
        for cred in db_credentials:
            store_secure_credential(
                credential_id=cred['id'],
                value=cred['value'],
                credential_type=cred['type'],
                user_id='db_tester'
            )
        
        print("✓ Database credentials setup complete")
    
    def secure_database_connection_test(self):
        """Example of secure database connection testing"""
        with secure_operation_context('db_tester', 'db_connection_test', 'mysql_database'):
            # Get connection string securely
            connection_string = get_secure_credential('mysql_connection', 'db_tester')
            
            if not connection_string:
                raise Exception("Failed to retrieve database connection string")
            
            # Use connection (never log actual connection string)
            print("Connecting to MySQL database...")
            
            # Log sanitized version
            safe_connection = sanitize_sensitive_data(f"Connection: {connection_string}")
            print(f"Safe log: {safe_connection}")
            
            # Simulate database operations
            print("✓ Secure database connection test completed")
    
    def mongodb_test_with_credential_rotation(self):
        """Example with credential rotation"""
        with secure_operation_context('db_tester', 'mongodb_test', 'mongodb_database'):
            # Check if credential needs rotation
            cred_store = self.security_manager.credential_store
            needs_rotation = cred_store.check_rotation_needed()
            
            if 'mongodb_connection' in needs_rotation:
                print("⚠️ MongoDB credentials need rotation")
                # In real scenario, you would rotate the credentials
                new_connection = 'mongodb://admin:NewMongoPass123@localhost:27017/testdb?authSource=admin'
                cred_store.rotate_credential('mongodb_connection', new_connection, 'db_tester')
                print("✓ MongoDB credentials rotated")
            
            # Get current connection
            connection = get_secure_credential('mongodb_connection', 'db_tester')
            print("✓ MongoDB test with rotation check completed")


class SecureAPITestExample:
    """Example of secure API testing with multiple authentication methods"""
    
    def __init__(self):
        self.security_manager = get_security_manager()
        register_security_user('api_tester', ['automation', 'user'])
    
    def setup_api_credentials(self):
        """Setup various API credentials"""
        api_credentials = [
            {
                'id': 'stripe_api_key',
                'value': 'sk_test_1234567890abcdef1234567890abcdef',
                'type': CredentialType.API_KEY,
                'description': 'Stripe API key for payment testing',
                'security_level': SecurityLevel.CRITICAL
            },
            {
                'id': 'oauth_client_secret',
                'value': 'oauth_secret_abcdef123456789',
                'type': CredentialType.CUSTOM,
                'description': 'OAuth client secret',
                'security_level': SecurityLevel.HIGH
            },
            {
                'id': 'jwt_signing_key',
                'value': 'super_secret_jwt_signing_key_2024',
                'type': CredentialType.CUSTOM,
                'description': 'JWT signing key for token validation',
                'security_level': SecurityLevel.CRITICAL
            }
        ]
        
        for cred in api_credentials:
            store_secure_credential(
                credential_id=cred['id'],
                value=cred['value'],
                credential_type=cred['type'],
                user_id='api_tester'
            )
        
        print("✓ API credentials setup complete")
    
    def secure_payment_api_test(self):
        """Example of secure payment API testing"""
        with secure_operation_context('api_tester', 'payment_test', 'stripe_api'):
            # Get Stripe API key
            api_key = get_secure_credential('stripe_api_key', 'api_tester')
            
            if not api_key:
                raise Exception("Failed to retrieve Stripe API key")
            
            # Simulate payment processing
            payment_data = {
                'amount': 1000,
                'currency': 'usd',
                'source': 'tok_visa'
            }
            
            # Log payment attempt (API key protected)
            log_data = f"Payment API call with key: {api_key} and data: {payment_data}"
            safe_log = sanitize_sensitive_data(log_data)
            print(f"Safe payment log: {safe_log}")
            
            print("✓ Secure payment API test completed")
    
    def oauth_flow_test(self):
        """Example of secure OAuth flow testing"""
        with secure_operation_context('api_tester', 'oauth_test', 'oauth_provider'):
            # Get OAuth credentials
            client_secret = get_secure_credential('oauth_client_secret', 'api_tester')
            
            if not client_secret:
                raise Exception("Failed to retrieve OAuth client secret")
            
            # Simulate OAuth flow
            oauth_request = {
                'client_id': 'test_client_id',
                'client_secret': client_secret,
                'grant_type': 'authorization_code',
                'code': 'test_auth_code'
            }
            
            # Check compliance before sending
            compliance_check = check_security_compliance(str(oauth_request))
            if not compliance_check['compliant']:
                print(f"⚠️ Compliance issues found: {compliance_check['findings']}")
            
            # Log safe version
            safe_request = sanitize_sensitive_data(str(oauth_request))
            print(f"OAuth request: {safe_request}")
            
            print("✓ Secure OAuth test completed")


class ComplianceTestingExample:
    """Example of compliance testing with security framework"""
    
    def __init__(self):
        self.security_manager = get_security_manager()
        register_security_user('compliance_tester', ['admin'])
    
    def gdpr_compliance_test(self):
        """Example of GDPR compliance testing"""
        print("\n=== GDPR Compliance Testing ===")
        
        # Test data that might contain PII
        test_datasets = [
            "User email: john.doe@example.com, Phone: +1-555-123-4567",
            "Customer ID: 12345, SSN: 123-45-6789",
            "Payment info: Card 4111-1111-1111-1111, CVV: 123",
            "Clean data without PII information"
        ]
        
        for i, data in enumerate(test_datasets):
            print(f"\nDataset {i+1}: {data}")
            
            # Check compliance
            compliance_report = check_security_compliance(data)
            
            print(f"  Compliant: {compliance_report['compliant']}")
            print(f"  Risk Level: {compliance_report['risk_level']}")
            
            if compliance_report['findings']:
                print(f"  Findings: {compliance_report['findings']}")
                print(f"  Recommendations: {compliance_report['recommendations']}")
                
                # Sanitize the data
                sanitized = sanitize_sensitive_data(data)
                print(f"  Sanitized: {sanitized}")
        
        print("✓ GDPR compliance testing completed")
    
    def audit_trail_test(self):
        """Example of audit trail testing"""
        print("\n=== Audit Trail Testing ===")
        
        # Perform various operations that should be audited
        operations = [
            ('store_credential', lambda: store_secure_credential(
                'audit_test_key', 'secret_value', CredentialType.API_KEY, 'compliance_tester'
            )),
            ('retrieve_credential', lambda: get_secure_credential(
                'audit_test_key', 'compliance_tester'
            )),
            ('failed_retrieval', lambda: get_secure_credential(
                'nonexistent_key', 'compliance_tester'
            ))
        ]
        
        for op_name, operation in operations:
            with secure_operation_context('compliance_tester', op_name, 'audit_test'):
                try:
                    result = operation()
                    print(f"  {op_name}: {'Success' if result else 'Failed'}")
                except Exception as e:
                    print(f"  {op_name}: Error - {e}")
        
        # Generate audit report
        audit_report = self.security_manager.generate_security_report()
        print(f"\nAudit Summary:")
        print(f"  Total Events: {audit_report['audit_trail']['total_events']}")
        print(f"  Failed Attempts: {audit_report['audit_trail']['failed_attempts']}")
        
        print("✓ Audit trail testing completed")


class VaultIntegrationExample:
    """Example of vault integration for production credentials"""
    
    def __init__(self):
        self.security_manager = get_security_manager()
        register_security_user('vault_admin', ['admin'])
    
    def setup_vault_integration(self):
        """Setup vault integration example"""
        print("\n=== Vault Integration Setup ===")
        
        # Example vault configurations (would be real in production)
        vault_configs = {
            'hashicorp': {
                'url': 'http://localhost:8200',
                'token': 'vault_token_example',
                'enabled': True
            },
            'aws': {
                'region': 'us-east-1',
                'enabled': False  # Disabled for example
            },
            'azure': {
                'vault_url': 'https://example-vault.vault.azure.net/',
                'enabled': False  # Disabled for example
            }
        }
        
        print("Vault configurations:")
        for vault_name, config in vault_configs.items():
            status = "Enabled" if config.get('enabled') else "Disabled"
            print(f"  {vault_name}: {status}")
        
        print("✓ Vault integration setup completed")
    
    def production_credential_workflow(self):
        """Example of production credential workflow with vault"""
        print("\n=== Production Credential Workflow ===")
        
        # In production, these would come from actual vaults
        production_secrets = [
            'prod_database_password',
            'prod_api_key',
            'prod_encryption_key'
        ]
        
        for secret_name in production_secrets:
            # Simulate vault retrieval
            print(f"  Retrieving {secret_name} from vault...")
            
            # In real implementation, this would use vault integration
            # vault_secret = vault.retrieve_secret(secret_name)
            
            # For now, demonstrate with local secure storage
            store_secure_credential(
                secret_name, 
                f"vault_retrieved_{secret_name}_value",
                CredentialType.CUSTOM,
                'vault_admin'
            )
            
            retrieved = get_secure_credential(secret_name, 'vault_admin')
            if retrieved:
                print(f"    ✓ {secret_name} retrieved successfully")
            else:
                print(f"    ✗ Failed to retrieve {secret_name}")
        
        print("✓ Production credential workflow completed")


def run_comprehensive_security_examples():
    """Run all security integration examples"""
    print("🔐 Starting Comprehensive Security Integration Examples")
    print("=" * 60)
    
    # Initialize security framework
    setup_security_framework()
    
    # Web testing examples
    print("\n1. Web Testing Security Examples")
    web_example = SecureWebTestExample()
    web_example.setup_test_credentials()
    web_example.secure_login_test()
    web_example.api_test_with_token()
    
    # Database testing examples
    print("\n2. Database Testing Security Examples")
    db_example = SecureDatabaseTestExample()
    db_example.setup_database_credentials()
    db_example.secure_database_connection_test()
    db_example.mongodb_test_with_credential_rotation()
    
    # API testing examples
    print("\n3. API Testing Security Examples")
    api_example = SecureAPITestExample()
    api_example.setup_api_credentials()
    api_example.secure_payment_api_test()
    api_example.oauth_flow_test()
    
    # Compliance testing examples
    print("\n4. Compliance Testing Examples")
    compliance_example = ComplianceTestingExample()
    compliance_example.gdpr_compliance_test()
    compliance_example.audit_trail_test()
    
    # Vault integration examples
    print("\n5. Vault Integration Examples")
    vault_example = VaultIntegrationExample()
    vault_example.setup_vault_integration()
    vault_example.production_credential_workflow()
    
    # Generate final security report
    print("\n6. Final Security Report")
    security_manager = get_security_manager()
    final_report = security_manager.generate_security_report()
    
    print(f"Security Framework Summary:")
    print(f"  Total Credentials: {final_report['credentials']['total_stored']}")
    print(f"  Active Users: {final_report['access_control']['total_users']}")
    print(f"  Audit Events: {final_report['audit_trail']['total_events']}")
    print(f"  Vault Integrations: {len(final_report['vault_integrations'])}")
    
    print("\n🎉 All security integration examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    run_comprehensive_security_examples()
