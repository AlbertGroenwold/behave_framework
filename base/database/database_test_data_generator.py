"""Database test data generator for automation testing"""

from typing import Dict, List, Union


class DatabaseTestDataGenerator:
    """Base test data generator for database testing"""
    
    @staticmethod
    def generate_user_data(count: int = 1) -> Union[Dict, List[Dict]]:
        """Generate user test data"""
        import random
        import string
        from datetime import datetime, timedelta
        
        def generate_single_user():
            username = ''.join(random.choices(string.ascii_lowercase, k=8))
            return {
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
    def generate_product_data(count: int = 1) -> Union[Dict, List[Dict]]:
        """Generate product test data"""
        import random
        
        def generate_single_product():
            return {
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
    def generate_order_data(count: int = 1) -> Union[Dict, List[Dict]]:
        """Generate order test data"""
        import random
        from datetime import datetime
        
        def generate_single_order():
            return {
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
