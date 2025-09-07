"""
Security Utilities Module for Central Quality Hub Framework

This module provides comprehensive security capabilities including:
- Secure credential storage and management
- Credential encryption and rotation
- Access control mechanisms
- Sensitive data protection
- Security audit trails
- Vault integrations (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault)
"""

import os
import base64
import hashlib
import secrets
import json
import logging
import threading
import time
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from contextlib import contextmanager
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
import re
import weakref
from abc import ABC, abstractmethod
from enum import Enum


class SecurityLevel(Enum):
    """Security levels for different operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CredentialType(Enum):
    """Types of credentials that can be managed"""
    PASSWORD = "password"
    API_KEY = "api_key"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    CONNECTION_STRING = "connection_string"
    SSH_KEY = "ssh_key"
    CUSTOM = "custom"


@dataclass
class CredentialInfo:
    """Information about a stored credential"""
    credential_id: str
    credential_type: CredentialType
    description: str
    created_at: datetime
    last_accessed: datetime
    rotation_interval: Optional[int] = None  # seconds
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)
    access_count: int = 0
    max_access_count: Optional[int] = None


@dataclass
class SecurityAuditEvent:
    """Security audit event"""
    event_id: str
    event_type: str
    timestamp: datetime
    user_id: str
    resource: str
    action: str
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class EncryptionManager:
    """Handle encryption and decryption operations"""
    
    def __init__(self, master_password: str = None):
        self.master_password = master_password or os.environ.get('SECURITY_MASTER_PASSWORD', 'default_key')
        self._fernet = None
        self._salt = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption with derived key"""
        # Generate or load salt
        salt_file = '.security_salt'
        if os.path.exists(salt_file):
            with open(salt_file, 'rb') as f:
                self._salt = f.read()
        else:
            self._salt = os.urandom(16)
            with open(salt_file, 'wb') as f:
                f.write(self._salt)
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
        self._fernet = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        try:
            encrypted_data = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise
    
    def generate_key(self) -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()
    
    def hash_password(self, password: str, salt: str = None) -> Dict[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return {
            'hash': password_hash.hex(),
            'salt': salt
        }
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return computed_hash.hex() == password_hash


class AccessController:
    """Manage access control for credentials and resources"""
    
    def __init__(self):
        self.permissions = {}
        self.roles = {}
        self.user_roles = {}
        self.access_log = []
        self.lock = threading.RLock()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def define_role(self, role_name: str, permissions: List[str]):
        """Define a role with specific permissions"""
        with self.lock:
            self.roles[role_name] = set(permissions)
        self.logger.info(f"Defined role '{role_name}' with permissions: {permissions}")
    
    def assign_role(self, user_id: str, role_name: str):
        """Assign role to user"""
        with self.lock:
            if role_name not in self.roles:
                raise ValueError(f"Role '{role_name}' not defined")
            
            if user_id not in self.user_roles:
                self.user_roles[user_id] = set()
            
            self.user_roles[user_id].add(role_name)
        
        self.logger.info(f"Assigned role '{role_name}' to user '{user_id}'")
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        with self.lock:
            if user_id not in self.user_roles:
                return False
            
            user_permissions = set()
            for role in self.user_roles[user_id]:
                if role in self.roles:
                    user_permissions.update(self.roles[role])
            
            has_permission = permission in user_permissions
            
            # Log access attempt
            self.access_log.append({
                'timestamp': datetime.now(),
                'user_id': user_id,
                'permission': permission,
                'granted': has_permission
            })
            
            return has_permission
    
    def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for a user"""
        with self.lock:
            if user_id not in self.user_roles:
                return set()
            
            permissions = set()
            for role in self.user_roles[user_id]:
                if role in self.roles:
                    permissions.update(self.roles[role])
            
            return permissions
    
    def revoke_role(self, user_id: str, role_name: str):
        """Revoke role from user"""
        with self.lock:
            if user_id in self.user_roles:
                self.user_roles[user_id].discard(role_name)
        
        self.logger.info(f"Revoked role '{role_name}' from user '{user_id}'")
    
    def get_access_log(self, user_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get access log for audit purposes"""
        with self.lock:
            log = self.access_log[-limit:]
            if user_id:
                log = [entry for entry in log if entry['user_id'] == user_id]
            return log


class SecureCredentialStore:
    """Secure storage for credentials with encryption and access control"""
    
    def __init__(self, encryption_manager: EncryptionManager, access_controller: AccessController):
        self.encryption_manager = encryption_manager
        self.access_controller = access_controller
        self.credentials = {}
        self.credential_info = {}
        self.lock = threading.RLock()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_default_permissions()
    
    def _setup_default_permissions(self):
        """Setup default permissions"""
        self.access_controller.define_role('admin', ['credential:read', 'credential:write', 'credential:delete', 'credential:rotate'])
        self.access_controller.define_role('user', ['credential:read'])
        self.access_controller.define_role('service', ['credential:read', 'credential:rotate'])
    
    def store_credential(self, credential_id: str, credential_value: str, 
                        credential_type: CredentialType, user_id: str,
                        description: str = "", security_level: SecurityLevel = SecurityLevel.MEDIUM,
                        rotation_interval: int = None, **metadata) -> bool:
        """Store encrypted credential"""
        if not self.access_controller.check_permission(user_id, 'credential:write'):
            self.logger.warning(f"User {user_id} denied credential write access")
            return False
        
        with self.lock:
            try:
                # Encrypt credential
                encrypted_value = self.encryption_manager.encrypt(credential_value)
                
                # Store encrypted credential
                self.credentials[credential_id] = encrypted_value
                
                # Store credential info
                self.credential_info[credential_id] = CredentialInfo(
                    credential_id=credential_id,
                    credential_type=credential_type,
                    description=description,
                    created_at=datetime.now(),
                    last_accessed=datetime.now(),
                    rotation_interval=rotation_interval,
                    security_level=security_level,
                    metadata=metadata
                )
                
                self.logger.info(f"Stored credential '{credential_id}' by user '{user_id}'")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to store credential '{credential_id}': {e}")
                return False
    
    def retrieve_credential(self, credential_id: str, user_id: str) -> Optional[str]:
        """Retrieve and decrypt credential"""
        if not self.access_controller.check_permission(user_id, 'credential:read'):
            self.logger.warning(f"User {user_id} denied credential read access")
            return None
        
        with self.lock:
            if credential_id not in self.credentials:
                return None
            
            try:
                # Update access info
                if credential_id in self.credential_info:
                    info = self.credential_info[credential_id]
                    info.last_accessed = datetime.now()
                    info.access_count += 1
                    
                    # Check access limits
                    if info.max_access_count and info.access_count > info.max_access_count:
                        self.logger.warning(f"Credential '{credential_id}' exceeded max access count")
                        return None
                
                # Decrypt credential
                encrypted_value = self.credentials[credential_id]
                decrypted_value = self.encryption_manager.decrypt(encrypted_value)
                
                self.logger.debug(f"Retrieved credential '{credential_id}' by user '{user_id}'")
                return decrypted_value
                
            except Exception as e:
                self.logger.error(f"Failed to retrieve credential '{credential_id}': {e}")
                return None
    
    def delete_credential(self, credential_id: str, user_id: str) -> bool:
        """Delete credential"""
        if not self.access_controller.check_permission(user_id, 'credential:delete'):
            self.logger.warning(f"User {user_id} denied credential delete access")
            return False
        
        with self.lock:
            if credential_id in self.credentials:
                del self.credentials[credential_id]
            if credential_id in self.credential_info:
                del self.credential_info[credential_id]
            
            self.logger.info(f"Deleted credential '{credential_id}' by user '{user_id}'")
            return True
    
    def rotate_credential(self, credential_id: str, new_value: str, user_id: str) -> bool:
        """Rotate credential with new value"""
        if not self.access_controller.check_permission(user_id, 'credential:rotate'):
            self.logger.warning(f"User {user_id} denied credential rotate access")
            return False
        
        with self.lock:
            if credential_id not in self.credentials:
                return False
            
            try:
                # Encrypt new value
                encrypted_value = self.encryption_manager.encrypt(new_value)
                self.credentials[credential_id] = encrypted_value
                
                # Update info
                if credential_id in self.credential_info:
                    info = self.credential_info[credential_id]
                    info.last_accessed = datetime.now()
                    info.access_count = 0  # Reset access count
                
                self.logger.info(f"Rotated credential '{credential_id}' by user '{user_id}'")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to rotate credential '{credential_id}': {e}")
                return False
    
    def list_credentials(self, user_id: str) -> List[Dict[str, Any]]:
        """List available credentials (without values)"""
        if not self.access_controller.check_permission(user_id, 'credential:read'):
            return []
        
        with self.lock:
            result = []
            for cred_id, info in self.credential_info.items():
                result.append({
                    'credential_id': cred_id,
                    'credential_type': info.credential_type.value,
                    'description': info.description,
                    'created_at': info.created_at.isoformat(),
                    'last_accessed': info.last_accessed.isoformat(),
                    'access_count': info.access_count,
                    'security_level': info.security_level.value
                })
            return result
    
    def check_rotation_needed(self) -> List[str]:
        """Check which credentials need rotation"""
        with self.lock:
            needs_rotation = []
            current_time = datetime.now()
            
            for cred_id, info in self.credential_info.items():
                if info.rotation_interval:
                    time_since_creation = (current_time - info.created_at).total_seconds()
                    if time_since_creation >= info.rotation_interval:
                        needs_rotation.append(cred_id)
            
            return needs_rotation


class SensitiveDataDetector:
    """Detect and handle sensitive data in logs and transmissions"""
    
    def __init__(self):
        self.patterns = {
            'password': [
                r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
                r'pwd["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
                r'pass["\']?\s*[:=]\s*["\']?([^"\'\s]+)'
            ],
            'api_key': [
                r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})',
                r'apikey["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})'
            ],
            'token': [
                r'token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9._-]{20,})',
                r'jwt["\']?\s*[:=]\s*["\']?([a-zA-Z0-9._-]{20,})'
            ],
            'connection_string': [
                r'connection[_-]?string["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
                r'conn[_-]?str["\']?\s*[:=]\s*["\']?([^"\'\s]+)'
            ],
            'email': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            'credit_card': [
                r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
            ],
            'ssn': [
                r'\b\d{3}-?\d{2}-?\d{4}\b'
            ]
        }
        self.compiled_patterns = {}
        self._compile_patterns()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _compile_patterns(self):
        """Compile regex patterns for performance"""
        for category, patterns in self.patterns.items():
            self.compiled_patterns[category] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def detect_sensitive_data(self, text: str) -> Dict[str, List[str]]:
        """Detect sensitive data in text"""
        findings = {}
        
        for category, patterns in self.compiled_patterns.items():
            matches = []
            for pattern in patterns:
                found = pattern.findall(text)
                matches.extend(found)
            
            if matches:
                findings[category] = matches
        
        return findings
    
    def sanitize_text(self, text: str, replacement: str = "***REDACTED***") -> str:
        """Sanitize text by replacing sensitive data"""
        sanitized = text
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                sanitized = pattern.sub(replacement, sanitized)
        
        return sanitized
    
    def mask_data(self, text: str, show_chars: int = 3) -> str:
        """Mask sensitive data showing only first few characters"""
        def mask_match(match):
            value = match.group(1) if match.groups() else match.group(0)
            if len(value) <= show_chars:
                return '*' * len(value)
            return value[:show_chars] + '*' * (len(value) - show_chars)
        
        masked = text
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                masked = pattern.sub(mask_match, masked)
        
        return masked
    
    def add_custom_pattern(self, category: str, pattern: str):
        """Add custom sensitive data pattern"""
        if category not in self.patterns:
            self.patterns[category] = []
            self.compiled_patterns[category] = []
        
        self.patterns[category].append(pattern)
        self.compiled_patterns[category].append(re.compile(pattern, re.IGNORECASE))
        
        self.logger.info(f"Added custom pattern for category '{category}'")


class SecurityAuditor:
    """Security audit trail and monitoring"""
    
    def __init__(self, max_events: int = 10000):
        self.max_events = max_events
        self.events = []
        self.lock = threading.RLock()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.alert_callbacks = []
    
    def add_alert_callback(self, callback: Callable[[SecurityAuditEvent], None]):
        """Add callback for security alerts"""
        self.alert_callbacks.append(callback)
    
    def log_event(self, event_type: str, user_id: str, resource: str, 
                  action: str, success: bool, details: Dict[str, Any] = None,
                  ip_address: str = None, user_agent: str = None) -> str:
        """Log security event"""
        event_id = secrets.token_hex(16)
        
        event = SecurityAuditEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.now(),
            user_id=user_id,
            resource=resource,
            action=action,
            success=success,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        with self.lock:
            self.events.append(event)
            
            # Maintain max events limit
            if len(self.events) > self.max_events:
                self.events.pop(0)
        
        # Trigger alerts for failed events
        if not success:
            self._trigger_alerts(event)
        
        self.logger.info(f"Security event logged: {event_type} - {action} by {user_id}")
        return event_id
    
    def _trigger_alerts(self, event: SecurityAuditEvent):
        """Trigger security alerts"""
        for callback in self.alert_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
    
    def get_events(self, event_type: str = None, user_id: str = None, 
                   start_time: datetime = None, end_time: datetime = None,
                   limit: int = 100) -> List[SecurityAuditEvent]:
        """Get filtered security events"""
        with self.lock:
            filtered_events = self.events
            
            if event_type:
                filtered_events = [e for e in filtered_events if e.event_type == event_type]
            
            if user_id:
                filtered_events = [e for e in filtered_events if e.user_id == user_id]
            
            if start_time:
                filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
            
            if end_time:
                filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
            
            return filtered_events[-limit:]
    
    def get_failed_attempts(self, time_window: int = 3600, limit: int = 50) -> List[SecurityAuditEvent]:
        """Get recent failed security attempts"""
        cutoff_time = datetime.now() - timedelta(seconds=time_window)
        
        with self.lock:
            failed_events = [
                event for event in self.events 
                if not event.success and event.timestamp >= cutoff_time
            ]
            
            return failed_events[-limit:]
    
    def export_audit_log(self, filepath: str, format: str = 'json'):
        """Export audit log to file"""
        with self.lock:
            if format.lower() == 'json':
                with open(filepath, 'w') as f:
                    events_data = []
                    for event in self.events:
                        event_dict = {
                            'event_id': event.event_id,
                            'event_type': event.event_type,
                            'timestamp': event.timestamp.isoformat(),
                            'user_id': event.user_id,
                            'resource': event.resource,
                            'action': event.action,
                            'success': event.success,
                            'details': event.details,
                            'ip_address': event.ip_address,
                            'user_agent': event.user_agent
                        }
                        events_data.append(event_dict)
                    
                    json.dump(events_data, f, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
        
        self.logger.info(f"Exported audit log to {filepath}")


class VaultIntegration(ABC):
    """Abstract base class for vault integrations"""
    
    @abstractmethod
    def store_secret(self, key: str, value: str, **kwargs) -> bool:
        """Store secret in vault"""
        pass
    
    @abstractmethod
    def retrieve_secret(self, key: str, **kwargs) -> Optional[str]:
        """Retrieve secret from vault"""
        pass
    
    @abstractmethod
    def delete_secret(self, key: str, **kwargs) -> bool:
        """Delete secret from vault"""
        pass
    
    @abstractmethod
    def list_secrets(self, **kwargs) -> List[str]:
        """List available secrets"""
        pass


class HashiCorpVaultIntegration(VaultIntegration):
    """HashiCorp Vault integration"""
    
    def __init__(self, vault_url: str, vault_token: str, mount_point: str = 'secret'):
        self.vault_url = vault_url.rstrip('/')
        self.vault_token = vault_token
        self.mount_point = mount_point
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Note: In real implementation, you would use hvac library
        self.logger.info(f"Initialized HashiCorp Vault integration: {vault_url}")
    
    def store_secret(self, key: str, value: str, **kwargs) -> bool:
        """Store secret in HashiCorp Vault"""
        try:
            # Mock implementation - replace with actual hvac calls
            self.logger.info(f"Storing secret '{key}' in HashiCorp Vault")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store secret in HashiCorp Vault: {e}")
            return False
    
    def retrieve_secret(self, key: str, **kwargs) -> Optional[str]:
        """Retrieve secret from HashiCorp Vault"""
        try:
            # Mock implementation - replace with actual hvac calls
            self.logger.info(f"Retrieving secret '{key}' from HashiCorp Vault")
            return None  # Would return actual secret
        except Exception as e:
            self.logger.error(f"Failed to retrieve secret from HashiCorp Vault: {e}")
            return None
    
    def delete_secret(self, key: str, **kwargs) -> bool:
        """Delete secret from HashiCorp Vault"""
        try:
            # Mock implementation - replace with actual hvac calls
            self.logger.info(f"Deleting secret '{key}' from HashiCorp Vault")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete secret from HashiCorp Vault: {e}")
            return False
    
    def list_secrets(self, **kwargs) -> List[str]:
        """List secrets from HashiCorp Vault"""
        try:
            # Mock implementation - replace with actual hvac calls
            self.logger.info("Listing secrets from HashiCorp Vault")
            return []
        except Exception as e:
            self.logger.error(f"Failed to list secrets from HashiCorp Vault: {e}")
            return []


class AWSSecretsManagerIntegration(VaultIntegration):
    """AWS Secrets Manager integration"""
    
    def __init__(self, region_name: str, aws_access_key_id: str = None, aws_secret_access_key: str = None):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Note: In real implementation, you would use boto3
        self.logger.info(f"Initialized AWS Secrets Manager integration: {region_name}")
    
    def store_secret(self, key: str, value: str, **kwargs) -> bool:
        """Store secret in AWS Secrets Manager"""
        try:
            # Mock implementation - replace with actual boto3 calls
            self.logger.info(f"Storing secret '{key}' in AWS Secrets Manager")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store secret in AWS Secrets Manager: {e}")
            return False
    
    def retrieve_secret(self, key: str, **kwargs) -> Optional[str]:
        """Retrieve secret from AWS Secrets Manager"""
        try:
            # Mock implementation - replace with actual boto3 calls
            self.logger.info(f"Retrieving secret '{key}' from AWS Secrets Manager")
            return None  # Would return actual secret
        except Exception as e:
            self.logger.error(f"Failed to retrieve secret from AWS Secrets Manager: {e}")
            return None
    
    def delete_secret(self, key: str, **kwargs) -> bool:
        """Delete secret from AWS Secrets Manager"""
        try:
            # Mock implementation - replace with actual boto3 calls
            self.logger.info(f"Deleting secret '{key}' from AWS Secrets Manager")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete secret from AWS Secrets Manager: {e}")
            return False
    
    def list_secrets(self, **kwargs) -> List[str]:
        """List secrets from AWS Secrets Manager"""
        try:
            # Mock implementation - replace with actual boto3 calls
            self.logger.info("Listing secrets from AWS Secrets Manager")
            return []
        except Exception as e:
            self.logger.error(f"Failed to list secrets from AWS Secrets Manager: {e}")
            return []


class AzureKeyVaultIntegration(VaultIntegration):
    """Azure Key Vault integration"""
    
    def __init__(self, vault_url: str, credential=None):
        self.vault_url = vault_url
        self.credential = credential
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Note: In real implementation, you would use azure-keyvault-secrets
        self.logger.info(f"Initialized Azure Key Vault integration: {vault_url}")
    
    def store_secret(self, key: str, value: str, **kwargs) -> bool:
        """Store secret in Azure Key Vault"""
        try:
            # Mock implementation - replace with actual Azure SDK calls
            self.logger.info(f"Storing secret '{key}' in Azure Key Vault")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store secret in Azure Key Vault: {e}")
            return False
    
    def retrieve_secret(self, key: str, **kwargs) -> Optional[str]:
        """Retrieve secret from Azure Key Vault"""
        try:
            # Mock implementation - replace with actual Azure SDK calls
            self.logger.info(f"Retrieving secret '{key}' from Azure Key Vault")
            return None  # Would return actual secret
        except Exception as e:
            self.logger.error(f"Failed to retrieve secret from Azure Key Vault: {e}")
            return None
    
    def delete_secret(self, key: str, **kwargs) -> bool:
        """Delete secret from Azure Key Vault"""
        try:
            # Mock implementation - replace with actual Azure SDK calls
            self.logger.info(f"Deleting secret '{key}' from Azure Key Vault")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete secret from Azure Key Vault: {e}")
            return False
    
    def list_secrets(self, **kwargs) -> List[str]:
        """List secrets from Azure Key Vault"""
        try:
            # Mock implementation - replace with actual Azure SDK calls
            self.logger.info("Listing secrets from Azure Key Vault")
            return []
        except Exception as e:
            self.logger.error(f"Failed to list secrets from Azure Key Vault: {e}")
            return []


class SecureConfigurationLoader:
    """Load configuration securely from various sources"""
    
    def __init__(self, credential_store: SecureCredentialStore, vault_integrations: Dict[str, VaultIntegration] = None):
        self.credential_store = credential_store
        self.vault_integrations = vault_integrations or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sensitive_detector = SensitiveDataDetector()
    
    def load_config_from_env(self, user_id: str, sanitize: bool = True) -> Dict[str, str]:
        """Load configuration from environment variables"""
        config = {}
        
        for key, value in os.environ.items():
            if sanitize:
                # Check for sensitive data
                findings = self.sensitive_detector.detect_sensitive_data(f"{key}={value}")
                if findings:
                    self.logger.warning(f"Sensitive data detected in environment variable: {key}")
                    continue
            
            config[key] = value
        
        self.logger.info(f"Loaded {len(config)} environment variables for user {user_id}")
        return config
    
    def load_config_from_file(self, filepath: str, user_id: str, sanitize: bool = True) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(filepath, 'r') as f:
                if filepath.endswith('.json'):
                    config = json.load(f)
                else:
                    # Simple key=value format
                    config = {}
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
            
            if sanitize:
                config = self._sanitize_config(config)
            
            self.logger.info(f"Loaded configuration from {filepath} for user {user_id}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load config from {filepath}: {e}")
            return {}
    
    def load_secret_from_vault(self, vault_name: str, secret_key: str, user_id: str) -> Optional[str]:
        """Load secret from configured vault"""
        if vault_name not in self.vault_integrations:
            self.logger.error(f"Vault '{vault_name}' not configured")
            return None
        
        vault = self.vault_integrations[vault_name]
        secret = vault.retrieve_secret(secret_key)
        
        if secret:
            self.logger.info(f"Retrieved secret '{secret_key}' from vault '{vault_name}' for user {user_id}")
        
        return secret
    
    def _sanitize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize configuration by removing sensitive data"""
        sanitized = {}
        
        for key, value in config.items():
            if isinstance(value, str):
                findings = self.sensitive_detector.detect_sensitive_data(f"{key}={value}")
                if findings:
                    self.logger.warning(f"Sensitive data detected in config key: {key}")
                    continue
            
            sanitized[key] = value
        
        return sanitized


class SecurityManager:
    """Main security manager orchestrating all security components"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize components
        self.encryption_manager = EncryptionManager(
            master_password=self.config.get('master_password')
        )
        self.access_controller = AccessController()
        self.credential_store = SecureCredentialStore(
            self.encryption_manager, 
            self.access_controller
        )
        self.sensitive_detector = SensitiveDataDetector()
        self.auditor = SecurityAuditor(
            max_events=self.config.get('max_audit_events', 10000)
        )
        
        # Initialize vault integrations
        self.vault_integrations = {}
        self._setup_vault_integrations()
        
        self.config_loader = SecureConfigurationLoader(
            self.credential_store,
            self.vault_integrations
        )
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Setup security monitoring
        self._setup_security_monitoring()
    
    def _setup_vault_integrations(self):
        """Setup vault integrations based on configuration"""
        vault_config = self.config.get('vaults', {})
        
        # HashiCorp Vault
        if 'hashicorp' in vault_config:
            hc_config = vault_config['hashicorp']
            self.vault_integrations['hashicorp'] = HashiCorpVaultIntegration(
                vault_url=hc_config.get('url'),
                vault_token=hc_config.get('token'),
                mount_point=hc_config.get('mount_point', 'secret')
            )
        
        # AWS Secrets Manager
        if 'aws' in vault_config:
            aws_config = vault_config['aws']
            self.vault_integrations['aws'] = AWSSecretsManagerIntegration(
                region_name=aws_config.get('region'),
                aws_access_key_id=aws_config.get('access_key_id'),
                aws_secret_access_key=aws_config.get('secret_access_key')
            )
        
        # Azure Key Vault
        if 'azure' in vault_config:
            azure_config = vault_config['azure']
            self.vault_integrations['azure'] = AzureKeyVaultIntegration(
                vault_url=azure_config.get('vault_url'),
                credential=azure_config.get('credential')
            )
    
    def _setup_security_monitoring(self):
        """Setup security monitoring and alerts"""
        def security_alert_handler(event: SecurityAuditEvent):
            self.logger.warning(f"Security alert: {event.event_type} - {event.action} failed for user {event.user_id}")
        
        self.auditor.add_alert_callback(security_alert_handler)
    
    def register_user(self, user_id: str, roles: List[str] = None):
        """Register user with roles"""
        roles = roles or ['user']
        for role in roles:
            self.access_controller.assign_role(user_id, role)
        
        self.auditor.log_event('user_management', 'system', user_id, 'register', True)
        self.logger.info(f"Registered user {user_id} with roles: {roles}")
    
    def store_credential(self, credential_id: str, credential_value: str, 
                        credential_type: CredentialType, user_id: str, **kwargs) -> bool:
        """Store credential securely"""
        success = self.credential_store.store_credential(
            credential_id, credential_value, credential_type, user_id, **kwargs
        )
        
        self.auditor.log_event('credential_management', user_id, credential_id, 'store', success)
        return success
    
    def get_credential(self, credential_id: str, user_id: str) -> Optional[str]:
        """Retrieve credential securely"""
        credential = self.credential_store.retrieve_credential(credential_id, user_id)
        success = credential is not None
        
        self.auditor.log_event('credential_management', user_id, credential_id, 'retrieve', success)
        return credential
    
    def sanitize_log_message(self, message: str) -> str:
        """Sanitize log message to remove sensitive data"""
        return self.sensitive_detector.sanitize_text(message)
    
    def check_data_compliance(self, data: str) -> Dict[str, Any]:
        """Check data for compliance issues"""
        findings = self.sensitive_detector.detect_sensitive_data(data)
        
        compliance_report = {
            'compliant': len(findings) == 0,
            'findings': findings,
            'risk_level': 'low' if len(findings) == 0 else 'high',
            'recommendations': []
        }
        
        if findings:
            compliance_report['recommendations'].append('Remove or encrypt sensitive data')
            compliance_report['recommendations'].append('Implement data masking')
        
        return compliance_report
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        return {
            'credentials': {
                'total_stored': len(self.credential_store.credentials),
                'needs_rotation': len(self.credential_store.check_rotation_needed())
            },
            'access_control': {
                'total_users': len(self.access_controller.user_roles),
                'total_roles': len(self.access_controller.roles),
                'recent_access_attempts': len(self.access_controller.get_access_log(limit=100))
            },
            'audit_trail': {
                'total_events': len(self.auditor.events),
                'failed_attempts': len(self.auditor.get_failed_attempts())
            },
            'vault_integrations': list(self.vault_integrations.keys()),
            'generated_at': datetime.now().isoformat()
        }
    
    @contextmanager
    def secure_operation(self, user_id: str, operation: str, resource: str):
        """Context manager for secure operations with auditing"""
        start_time = datetime.now()
        success = False
        error = None
        
        try:
            yield
            success = True
        except Exception as e:
            error = str(e)
            raise
        finally:
            self.auditor.log_event(
                'secure_operation', 
                user_id, 
                resource, 
                operation, 
                success,
                details={'error': error, 'duration': (datetime.now() - start_time).total_seconds()}
            )


# Global security manager instance
_global_security_manager = None


def get_security_manager(config: Dict[str, Any] = None) -> SecurityManager:
    """Get global security manager instance"""
    global _global_security_manager
    if _global_security_manager is None:
        _global_security_manager = SecurityManager(config)
    return _global_security_manager


# Convenience functions
def store_secure_credential(credential_id: str, value: str, credential_type: CredentialType, user_id: str) -> bool:
    """Store credential using global security manager"""
    return get_security_manager().store_credential(credential_id, value, credential_type, user_id)


def get_secure_credential(credential_id: str, user_id: str) -> Optional[str]:
    """Get credential using global security manager"""
    return get_security_manager().get_credential(credential_id, user_id)


def sanitize_sensitive_data(text: str) -> str:
    """Sanitize text using global security manager"""
    return get_security_manager().sanitize_log_message(text)


def check_security_compliance(data: str) -> Dict[str, Any]:
    """Check compliance using global security manager"""
    return get_security_manager().check_data_compliance(data)


def secure_operation_context(user_id: str, operation: str, resource: str):
    """Context manager for secure operations"""
    return get_security_manager().secure_operation(user_id, operation, resource)


def register_security_user(user_id: str, roles: List[str] = None):
    """Register user with security manager"""
    return get_security_manager().register_user(user_id, roles)


def generate_security_audit_report() -> Dict[str, Any]:
    """Generate security audit report"""
    return get_security_manager().generate_security_report()
