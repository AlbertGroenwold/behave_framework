"""Database test data generator for automation testing with caching support"""

import time
import threading
import logging
import uuid
import json
import random
from typing import Dict, List, Union, Optional, Any, Callable
from datetime import datetime, timedelta
from ..utilities.cache_manager import CacheManager, MemoryCacheBackend, cache_test_data


class TestDataCache:
    """Specialized cache for test data with TTL and performance metrics."""
    
    def __init__(self, default_ttl: float = 3600, max_size: int = 500):
        self.cache_manager = CacheManager(
            backend=MemoryCacheBackend(max_size=max_size),
            enable_stats=True
        )
        self.default_ttl = default_ttl
        self.warming_enabled = False
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Performance metrics specific to test data
        self.performance_metrics = {
            'cache_warming_time': 0.0,
            'data_generation_time': 0.0,
            'cache_persistence_enabled': False,
            'last_warming_time': None
        }
        self._metrics_lock = threading.Lock()
    
    def enable_cache_warming(self):
        """Enable cache warming for frequently used test data."""
        self.warming_enabled = True
        self.cache_manager.enable_warming()
        
        # Register warming functions for common test data
        self.cache_manager.register_warming_function(
            'common_users', lambda: self._generate_common_users()
        )
        self.cache_manager.register_warming_function(
            'common_products', lambda: self._generate_common_products()
        )
        self.cache_manager.register_warming_function(
            'common_orders', lambda: self._generate_common_orders()
        )
        
        self.logger.info("Test data cache warming enabled")
    
    def warm_cache(self):
        """Warm up cache with frequently used test data."""
        if not self.warming_enabled:
            return
        
        start_time = time.time()
        self.cache_manager.warm_cache()
        warming_time = time.time() - start_time
        
        with self._metrics_lock:
            self.performance_metrics['cache_warming_time'] = warming_time
            self.performance_metrics['last_warming_time'] = datetime.now()
        
        self.logger.info(f"Test data cache warmed in {warming_time:.4f}s")
    
    def get_cached_data(self, key: str, generator_func: Callable, 
                       ttl: Optional[float] = None) -> Any:
        """Get data from cache or generate and cache it."""
        cache_key = f"test_data:{key}"
        ttl = ttl or self.default_ttl
        
        # Try to get from cache first
        cached_data = self.cache_manager.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        # Generate data and cache it
        start_time = time.time()
        data = generator_func()
        generation_time = time.time() - start_time
        
        with self._metrics_lock:
            self.performance_metrics['data_generation_time'] += generation_time
        
        self.cache_manager.set(cache_key, data, ttl)
        self.logger.debug(f"Generated and cached test data for key: {key}")
        
        return data
    
    def invalidate_test_data(self, pattern: str = "test_data"):
        """Invalidate cached test data matching pattern."""
        self.cache_manager.invalidate_pattern(pattern)
        self.logger.info(f"Invalidated test data cache with pattern: {pattern}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        with self._metrics_lock:
            base_stats = self.cache_manager.get_stats()
            base_stats.update(self.performance_metrics.copy())
        
        return base_stats
    
    def _generate_common_users(self) -> List[Dict]:
        """Generate common user data for warming."""
        return DatabaseTestDataGenerator.generate_user_data(10)
    
    def _generate_common_products(self) -> List[Dict]:
        """Generate common product data for warming."""
        return DatabaseTestDataGenerator.generate_product_data(10)
    
    def _generate_common_orders(self) -> List[Dict]:
        """Generate common order data for warming."""
        return DatabaseTestDataGenerator.generate_order_data(10)


class CacheAwareDataReader:
    """Data reader that leverages caching for performance."""
    
    def __init__(self, cache: TestDataCache):
        self.cache = cache
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def read_user_templates(self, template_type: str = "default") -> List[Dict]:
        """Read user data templates with caching."""
        return self.cache.get_cached_data(
            f"user_templates:{template_type}",
            lambda: self._load_user_templates(template_type),
            ttl=7200  # 2 hours
        )
    
    def read_product_templates(self, category: str = "default") -> List[Dict]:
        """Read product data templates with caching."""
        return self.cache.get_cached_data(
            f"product_templates:{category}",
            lambda: self._load_product_templates(category),
            ttl=7200  # 2 hours
        )
    
    def read_test_datasets(self, dataset_name: str) -> Dict[str, Any]:
        """Read test datasets with caching."""
        return self.cache.get_cached_data(
            f"test_datasets:{dataset_name}",
            lambda: self._load_test_dataset(dataset_name),
            ttl=3600  # 1 hour
        )
    
    def _load_user_templates(self, template_type: str) -> List[Dict]:
        """Load user templates (placeholder implementation)."""
        # This would typically load from files or database
        return [
            {"template": template_type, "type": "user", "count": 5},
            {"template": template_type, "type": "admin", "count": 2}
        ]
    
    def _load_product_templates(self, category: str) -> List[Dict]:
        """Load product templates (placeholder implementation)."""
        # This would typically load from files or database
        return [
            {"template": category, "type": "physical", "count": 10},
            {"template": category, "type": "digital", "count": 5}
        ]
    
    def _load_test_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """Load test dataset (placeholder implementation)."""
        # This would typically load from files or database
        return {
            "name": dataset_name,
            "records": 100,
            "created": datetime.now(),
            "data": f"Sample data for {dataset_name}"
        }


class RealisticDataPattern:
    """Patterns for generating realistic test data."""
    
    FIRST_NAMES = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'James', 'Lisa', 'Robert', 'Mary']
    LAST_NAMES = ['Smith', 'Johnson', 'Brown', 'Davis', 'Wilson', 'Miller', 'Moore', 'Taylor', 'Anderson', 'Thomas']
    CITIES = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
    STATES = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'FL', 'OH', 'NC', 'MI']
    COMPANIES = ['TechCorp', 'DataSystems', 'CloudWorks', 'InnovateLabs', 'GlobalTech', 'SmartSolutions', 'NextGen', 'FutureSoft']
    PRODUCT_CATEGORIES = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Automotive', 'Health', 'Beauty']
    EMAIL_DOMAINS = ['gmail.com', 'yahoo.com', 'outlook.com', 'company.com', 'test.com']


class DataRelationshipManager:
    """Manages relationships between generated data entities."""
    
    def __init__(self):
        self.relationships: Dict[str, List[str]] = {}
        self.foreign_keys: Dict[str, str] = {}
        self.reference_data: Dict[str, List[Any]] = {}
    
    def define_relationship(self, parent_entity: str, child_entity: str, foreign_key: str):
        """Define a parent-child relationship between entities."""
        if parent_entity not in self.relationships:
            self.relationships[parent_entity] = []
        self.relationships[parent_entity].append(child_entity)
        self.foreign_keys[f"{child_entity}_{foreign_key}"] = parent_entity
    
    def set_reference_data(self, entity: str, data: List[Any]):
        """Set reference data for an entity."""
        self.reference_data[entity] = data
    
    def get_random_reference(self, entity: str, field: str = 'id') -> Any:
        """Get a random reference from an entity."""
        if entity not in self.reference_data or not self.reference_data[entity]:
            return None
        
        import random
        item = random.choice(self.reference_data[entity])
        if isinstance(item, dict) and field in item:
            return item[field]
        return item


class DataValidationRules:
    """Validation rules for generated test data."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        import re
        pattern = r'^\+?1?[-.\s]?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]) -> bool:
        """Validate that required fields are present and not None."""
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                return False
        return True
    
    @staticmethod
    def validate_data_types(data: Dict, type_mapping: Dict[str, type]) -> bool:
        """Validate data types of fields."""
        for field, expected_type in type_mapping.items():
            if field in data and not isinstance(data[field], expected_type):
                return False
        return True


class DatabaseTestDataGenerator:
    """Enhanced test data generator with caching support"""
    
    def __init__(self, enable_caching: bool = True, cache_ttl: float = 3600):
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        
        if enable_caching:
            self.cache = TestDataCache(default_ttl=cache_ttl)
            self.data_reader = CacheAwareDataReader(self.cache)
        else:
            self.cache = None
            self.data_reader = None
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Enhanced features
        self.relationship_manager = DataRelationshipManager()
        self.validation_rules = DataValidationRules()
        self.realistic_patterns = RealisticDataPattern()
        
        # Setup default relationships
        self._setup_default_relationships()
    
    def enable_cache_warming(self):
        """Enable cache warming if caching is enabled."""
        if self.cache:
            self.cache.enable_cache_warming()
            self.cache.warm_cache()
    
    def generate_realistic_user_data(self, count: int = 1, cache_key: Optional[str] = None, 
                                   use_cache: bool = True) -> Union[Dict, List[Dict]]:
        """Generate realistic user test data with patterns."""
        if self.enable_caching and use_cache and cache_key:
            return self.cache.get_cached_data(
                f"realistic_users:{cache_key}:{count}",
                lambda: self._generate_realistic_user_data_internal(count),
                self.cache_ttl
            )
        else:
            return self._generate_realistic_user_data_internal(count)
    
    def generate_related_data(self, entity_type: str, parent_data: List[Dict], 
                            count_per_parent: int = 1) -> List[Dict]:
        """Generate related data based on parent entities."""
        related_data = []
        
        for parent in parent_data:
            parent_id = parent.get('id') or parent.get('user_id') or parent.get('customer_id')
            
            for _ in range(count_per_parent):
                if entity_type == 'order':
                    order_data = self._generate_order_data_internal(1)
                    if isinstance(order_data, list):
                        order_data = order_data[0]
                    order_data['customer_id'] = parent_id
                    related_data.append(order_data)
                
                elif entity_type == 'address':
                    address_data = {
                        'user_id': parent_id,
                        'street': f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'First St', 'Park Rd'])}",
                        'city': random.choice(self.realistic_patterns.CITIES),
                        'state': random.choice(self.realistic_patterns.STATES),
                        'zip_code': f"{random.randint(10000, 99999)}",
                        'is_primary': random.choice([True, False])
                    }
                    related_data.append(address_data)
        
        return related_data
    
    def validate_generated_data(self, data: Any, entity_type: str) -> bool:
        """Validate generated data against predefined rules."""
        if isinstance(data, list):
            return all(self.validate_generated_data(item, entity_type) for item in data)
        
        if not isinstance(data, dict):
            return False
        
        # Entity-specific validation
        if entity_type == 'user':
            required_fields = ['username', 'email', 'first_name', 'last_name']
            type_mapping = {
                'username': str,
                'email': str,
                'first_name': str,
                'last_name': str,
                'age': int
            }
            
            if not self.validation_rules.validate_required_fields(data, required_fields):
                return False
            
            if not self.validation_rules.validate_data_types(data, type_mapping):
                return False
            
            if 'email' in data and not self.validation_rules.validate_email(data['email']):
                return False
        
        elif entity_type == 'product':
            required_fields = ['name', 'price', 'category']
            type_mapping = {
                'name': str,
                'price': (int, float),
                'category': str,
                'quantity': int
            }
            
            if not self.validation_rules.validate_required_fields(data, required_fields):
                return False
            
            if not self.validation_rules.validate_data_types(data, type_mapping):
                return False
        
        return True
    
    def create_data_template(self, template_name: str, template_data: Dict, 
                           entity_type: str) -> str:
        """Create a reusable data template."""
        if not hasattr(self, '_templates'):
            self._templates = {}
        
        template_id = f"{template_name}_{uuid.uuid4().hex[:8]}"
        self._templates[template_id] = {
            'name': template_name,
            'data': template_data,
            'entity_type': entity_type,
            'created_at': datetime.now()
        }
        
        self.logger.info(f"Created data template: {template_name} ({template_id})")
        return template_id
    
    def generate_from_template(self, template_id: str, count: int = 1, 
                             **context) -> Union[Dict, List[Dict]]:
        """Generate data from a template with context substitution."""
        if not hasattr(self, '_templates') or template_id not in self._templates:
            raise ValueError(f"Template not found: {template_id}")
        
        template = self._templates[template_id]
        template_data = template['data'].copy()
        
        # Apply context substitution
        for key, value in context.items():
            if f"${{{key}}}" in str(template_data):
                template_data = json.loads(
                    json.dumps(template_data).replace(f"${{{key}}}", str(value))
                )
        
        if count == 1:
            return template_data
        else:
            return [template_data.copy() for _ in range(count)]
    
    def generate_user_data(self, count: int = 1, cache_key: Optional[str] = None, 
                          use_cache: bool = True) -> Union[Dict, List[Dict]]:
        """Generate user test data with optional caching"""
        if self.enable_caching and use_cache and cache_key:
            return self.cache.get_cached_data(
                f"users:{cache_key}:{count}",
                lambda: self._generate_user_data_internal(count),
                self.cache_ttl
            )
        else:
            return self._generate_user_data_internal(count)
    
    def generate_product_data(self, count: int = 1, cache_key: Optional[str] = None,
                             use_cache: bool = True) -> Union[Dict, List[Dict]]:
        """Generate product test data with optional caching"""
        if self.enable_caching and use_cache and cache_key:
            return self.cache.get_cached_data(
                f"products:{cache_key}:{count}",
                lambda: self._generate_product_data_internal(count),
                self.cache_ttl
            )
        else:
            return self._generate_product_data_internal(count)
    
    def generate_order_data(self, count: int = 1, cache_key: Optional[str] = None,
                           use_cache: bool = True) -> Union[Dict, List[Dict]]:
        """Generate order test data with optional caching"""
        if self.enable_caching and use_cache and cache_key:
            return self.cache.get_cached_data(
                f"orders:{cache_key}:{count}",
                lambda: self._generate_order_data_internal(count),
                self.cache_ttl
            )
        else:
            return self._generate_order_data_internal(count)
    
    def get_cache_performance_metrics(self) -> Optional[Dict[str, Any]]:
        """Get cache performance metrics."""
        if self.cache:
            return self.cache.get_performance_metrics()
        return None
    
    def invalidate_cache(self, pattern: str = "test_data"):
        """Invalidate cached test data."""
        if self.cache:
            self.cache.invalidate_test_data(pattern)
    
    def persist_cache_between_runs(self, enable: bool = True):
        """Enable/disable cache persistence between test runs."""
        if self.cache:
            with self.cache._metrics_lock:
                self.cache.performance_metrics['cache_persistence_enabled'] = enable
            self.logger.info(f"Cache persistence {'enabled' if enable else 'disabled'}")
    
    def _setup_default_relationships(self):
        """Setup default entity relationships."""
        # User -> Orders relationship
        self.relationship_manager.define_relationship('user', 'order', 'customer_id')
        
        # User -> Addresses relationship
        self.relationship_manager.define_relationship('user', 'address', 'user_id')
        
        # Product -> Order Items relationship
        self.relationship_manager.define_relationship('product', 'order_item', 'product_id')
        
        self.logger.debug("Default relationships configured")
    
    def _generate_realistic_user_data_internal(self, count: int = 1) -> Union[Dict, List[Dict]]:
        """Generate realistic user test data with patterns."""
        import random
        
        def generate_realistic_user():
            first_name = random.choice(self.realistic_patterns.FIRST_NAMES)
            last_name = random.choice(self.realistic_patterns.LAST_NAMES)
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
            email_domain = random.choice(self.realistic_patterns.EMAIL_DOMAINS)
            
            return {
                'id': random.randint(1000, 9999),
                'username': username,
                'email': f"{username}@{email_domain}",
                'first_name': first_name,
                'last_name': last_name,
                'age': random.randint(18, 80),
                'phone': f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
                'city': random.choice(self.realistic_patterns.CITIES),
                'state': random.choice(self.realistic_patterns.STATES),
                'company': random.choice(self.realistic_patterns.COMPANIES),
                'is_active': random.choice([True, True, True, False]),  # 75% active
                'created_date': datetime.now() - timedelta(days=random.randint(0, 365)),
                'last_login': datetime.now() - timedelta(days=random.randint(0, 30))
            }
        
        if count == 1:
            return generate_realistic_user()
        else:
            return [generate_realistic_user() for _ in range(count)]
    
    @staticmethod
    def _generate_user_data_internal(count: int = 1) -> Union[Dict, List[Dict]]:
        """Internal method to generate user test data"""
        import random
        import string
        
        def generate_single_user():
            username = ''.join(random.choices(string.ascii_lowercase, k=8))
            return {
                'id': random.randint(1000, 9999),
                'username': f"test_{username}",
                'email': f"{username}@testmail.com",
                'first_name': random.choice(['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emma']),
                'last_name': random.choice(['Smith', 'Johnson', 'Brown', 'Davis', 'Wilson', 'Miller']),
                'age': random.randint(18, 80),
                'is_active': random.choice([True, False]),
                'created_date': datetime.now() - timedelta(days=random.randint(0, 365))
            }
        
        if count == 1:
            return generate_single_user()
        else:
            return [generate_single_user() for _ in range(count)]
    
    @staticmethod
    def _generate_product_data_internal(count: int = 1) -> Union[Dict, List[Dict]]:
        """Internal method to generate product test data"""
        import random
        
        def generate_single_product():
            return {
                'id': random.randint(1000, 9999),
                'name': f"Test Product {random.randint(1, 1000)}",
                'description': f"Description for test product {random.randint(1, 1000)}",
                'price': round(random.uniform(10, 1000), 2),
                'category': random.choice(['Electronics', 'Clothing', 'Books', 'Home', 'Sports']),
                'in_stock': random.choice([True, False]),
                'quantity': random.randint(0, 100),
                'sku': f"SKU-{random.randint(10000, 99999)}"
            }
        
        if count == 1:
            return generate_single_product()
        else:
            return [generate_single_product() for _ in range(count)]
    
    @staticmethod
    def _generate_order_data_internal(count: int = 1) -> Union[Dict, List[Dict]]:
        """Internal method to generate order test data"""
        import random
        
        def generate_single_order():
            return {
                'id': random.randint(1000, 9999),
                'order_number': f"ORD-{random.randint(10000, 99999)}",
                'customer_id': random.randint(1, 100),
                'total_amount': round(random.uniform(50, 500), 2),
                'status': random.choice(['pending', 'processing', 'shipped', 'delivered', 'cancelled']),
                'order_date': datetime.now(),
                'shipping_address': f"{random.randint(100, 9999)} Test Street, Test City, TC {random.randint(10000, 99999)}"
            }
        
        if count == 1:
            return generate_single_order()
        else:
            return [generate_single_order() for _ in range(count)]


# Add necessary imports at the top of the file
import uuid
import json


# Convenience decorators for cached test data generation
def cached_user_data(cache_ttl: float = 3600):
    """Decorator for caching user data generation."""
    def decorator(func):
        cache_manager = CacheManager()
        return cache_test_data(cache_manager, ttl=cache_ttl)(func)
    return decorator


def cached_product_data(cache_ttl: float = 3600):
    """Decorator for caching product data generation."""
    def decorator(func):
        cache_manager = CacheManager()
        return cache_test_data(cache_manager, ttl=cache_ttl)(func)
    return decorator


def cached_order_data(cache_ttl: float = 3600):
    """Decorator for caching order data generation."""
    def decorator(func):
        cache_manager = CacheManager()
        return cache_test_data(cache_manager, ttl=cache_ttl)(func)
    return decorator


# Global test data generator instance
_global_generator = None


def get_global_test_data_generator() -> DatabaseTestDataGenerator:
    """Get global test data generator with caching enabled."""
    global _global_generator
    if _global_generator is None:
        _global_generator = DatabaseTestDataGenerator(enable_caching=True)
        _global_generator.enable_cache_warming()
    return _global_generator


# Convenience functions for global cached data generation
def generate_cached_users(count: int = 1, cache_key: str = "default") -> Union[Dict, List[Dict]]:
    """Generate cached user data using global generator."""
    return get_global_test_data_generator().generate_user_data(count, cache_key)


def generate_cached_products(count: int = 1, cache_key: str = "default") -> Union[Dict, List[Dict]]:
    """Generate cached product data using global generator."""
    return get_global_test_data_generator().generate_product_data(count, cache_key)


def generate_cached_orders(count: int = 1, cache_key: str = "default") -> Union[Dict, List[Dict]]:
    """Generate cached order data using global generator."""
    return get_global_test_data_generator().generate_order_data(count, cache_key)
