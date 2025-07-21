from behave import given, when, then
import sys
import os
import time

# Add the base directory to Python path
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from database.base_database_manager import DatabaseTestValidator, DatabasePerformanceMonitor, DatabaseTestDataGenerator
from database.database_managers import PostgreSQLManager, MySQLManager, SQLiteManager, MongoDBManager, RedisManager


@given('the database is connected and accessible')
def step_database_connected(context):
    """Verify database connection"""
    # Initialize database manager based on configuration
    if not hasattr(context, 'db_manager'):
        db_type = getattr(context, 'db_type', 'postgresql')  # Default to PostgreSQL
        
        if db_type == 'postgresql':
            context.db_manager = PostgreSQLManager('config/database_config.ini')
        elif db_type == 'mysql':
            context.db_manager = MySQLManager('config/database_config.ini')
        elif db_type == 'sqlite':
            context.db_manager = SQLiteManager('config/database_config.ini')
        elif db_type == 'mongodb':
            context.db_manager = MongoDBManager('config/database_config.ini')
        elif db_type == 'redis':
            context.db_manager = RedisManager('config/database_config.ini')
        else:
            context.db_manager = PostgreSQLManager('config/database_config.ini')
    
    # Connect to database
    assert context.db_manager.connect(), "Failed to connect to database"
    
    # Initialize performance monitor
    context.performance_monitor = DatabasePerformanceMonitor(context.db_manager)


@given('I have valid user data')
def step_have_valid_user_data(context):
    """Setup valid user data from table"""
    context.user_data = {}
    for row in context.table:
        field = row['field']
        value = row['value']
        
        # Convert numeric fields
        if field == 'age':
            value = int(value)
        
        context.user_data[field] = value


@given('I have an existing user in the database')
def step_have_existing_user(context):
    """Create existing user for testing"""
    # Generate test user data
    test_user = DatabaseTestDataGenerator.generate_user_data()
    
    if context.db_manager.db_type == 'mongodb':
        # MongoDB insertion
        result = context.db_manager.execute_query(
            collection_name='users',
            operation='insert_one',
            document=test_user
        )
        assert result['success'], "Failed to create test user"
        context.existing_user_id = result['inserted_id']
    else:
        # SQL database insertion
        fields = ', '.join(test_user.keys())
        placeholders = ', '.join([f":{key}" for key in test_user.keys()])
        query = f"INSERT INTO users ({fields}) VALUES ({placeholders})"
        
        result = context.db_manager.execute_query(query, test_user)
        assert result['success'], "Failed to create test user"
    
    context.existing_user = test_user


@given('I have an existing user to delete')
def step_have_existing_user_to_delete(context):
    """Create user specifically for deletion testing"""
    # Generate test user data for deletion
    delete_user = DatabaseTestDataGenerator.generate_user_data()
    delete_user['username'] = 'delete_test_user'
    
    if context.db_manager.db_type == 'mongodb':
        result = context.db_manager.execute_query(
            collection_name='users',
            operation='insert_one',
            document=delete_user
        )
        assert result['success'], "Failed to create user for deletion"
        context.delete_user_id = result['inserted_id']
    else:
        fields = ', '.join(delete_user.keys())
        placeholders = ', '.join([f":{key}" for key in delete_user.keys()])
        query = f"INSERT INTO users ({fields}) VALUES ({placeholders})"
        
        result = context.db_manager.execute_query(query, delete_user)
        assert result['success'], "Failed to create user for deletion"
        
        # Get the created user ID
        select_query = "SELECT id FROM users WHERE username = :username"
        select_result = context.db_manager.execute_query(select_query, {'username': delete_user['username']})
        if select_result['success'] and select_result['data']:
            context.delete_user_id = select_result['data'][0]['id']
    
    context.delete_user = delete_user


@given('I have user data with invalid email format')
def step_have_invalid_email_data(context):
    """Setup user data with invalid email"""
    context.invalid_user_data = {
        'username': 'invalid_email_user',
        'email': 'invalid-email-format',  # Invalid email
        'first_name': 'Invalid',
        'last_name': 'Email',
        'age': 25
    }


@given('the users table has at least {min_records:d} records')
def step_ensure_minimum_records(context, min_records):
    """Ensure table has minimum number of records"""
    current_count = context.db_manager.get_row_count('users')
    
    if current_count < min_records:
        # Generate additional records
        records_needed = min_records - current_count
        users_to_create = DatabaseTestDataGenerator.generate_user_data(records_needed)
        
        if context.db_manager.db_type == 'mongodb':
            context.db_manager.execute_query(
                collection_name='users',
                operation='insert_many',
                document=users_to_create
            )
        else:
            for user in users_to_create:
                fields = ', '.join(user.keys())
                placeholders = ', '.join([f":{key}" for key in user.keys()])
                query = f"INSERT INTO users ({fields}) VALUES ({placeholders})"
                context.db_manager.execute_query(query, user)


@given('I start a database transaction')
def step_start_transaction(context):
    """Start database transaction"""
    # Transaction handling would depend on the database type
    context.transaction_started = True


@given('multiple database connections are established')
def step_establish_multiple_connections(context):
    """Establish multiple database connections"""
    context.connections = []
    for i in range(3):  # Create 3 connections
        if context.db_manager.db_type == 'postgresql':
            conn = PostgreSQLManager('config/database_config.ini')
        elif context.db_manager.db_type == 'mysql':
            conn = MySQLManager('config/database_config.ini')
        else:
            conn = SQLiteManager('config/database_config.ini')
        
        assert conn.connect(), f"Failed to establish connection {i+1}"
        context.connections.append(conn)


@given('I have a database with test data')
def step_have_database_with_test_data(context):
    """Ensure database has test data"""
    # Create some test data
    test_users = DatabaseTestDataGenerator.generate_user_data(5)
    context.test_data_count = len(test_users)
    
    if context.db_manager.db_type == 'mongodb':
        context.db_manager.execute_query(
            collection_name='users',
            operation='insert_many',
            document=test_users
        )
    else:
        for user in test_users:
            fields = ', '.join(user.keys())
            placeholders = ', '.join([f":{key}" for key in user.keys()])
            query = f"INSERT INTO users ({fields}) VALUES ({placeholders})"
            context.db_manager.execute_query(query, user)


@when('I insert the user data into the users table')
def step_insert_user_data(context):
    """Insert user data into database"""
    if context.db_manager.db_type == 'mongodb':
        context.insert_result = context.db_manager.execute_query(
            collection_name='users',
            operation='insert_one',
            document=context.user_data
        )
    else:
        fields = ', '.join(context.user_data.keys())
        placeholders = ', '.join([f":{key}" for key in context.user_data.keys()])
        query = f"INSERT INTO users ({fields}) VALUES ({placeholders})"
        
        context.insert_result = context.performance_monitor.execute_timed_query(query, context.user_data)


@when('I update the user\'s email to "{new_email}"')
def step_update_user_email(context, new_email):
    """Update user's email"""
    if context.db_manager.db_type == 'mongodb':
        context.update_result = context.db_manager.execute_query(
            collection_name='users',
            operation='update_one',
            query={'username': context.existing_user['username']},
            update={'$set': {'email': new_email}}
        )
    else:
        query = "UPDATE users SET email = :email WHERE username = :username"
        params = {'email': new_email, 'username': context.existing_user['username']}
        context.update_result = context.performance_monitor.execute_timed_query(query, params)
    
    context.new_email = new_email


@when('I update the user\'s age to {new_age:d}')
def step_update_user_age(context, new_age):
    """Update user's age"""
    if context.db_manager.db_type == 'mongodb':
        context.db_manager.execute_query(
            collection_name='users',
            operation='update_one',
            query={'username': context.existing_user['username']},
            update={'$set': {'age': new_age}}
        )
    else:
        query = "UPDATE users SET age = :age WHERE username = :username"
        params = {'age': new_age, 'username': context.existing_user['username']}
        context.db_manager.execute_query(query, params)
    
    context.new_age = new_age


@when('I delete the user from the database')
def step_delete_user(context):
    """Delete user from database"""
    if context.db_manager.db_type == 'mongodb':
        context.delete_result = context.db_manager.execute_query(
            collection_name='users',
            operation='delete_one',
            query={'_id': context.delete_user_id}
        )
    else:
        query = "DELETE FROM users WHERE id = :id"
        params = {'id': context.delete_user_id}
        context.delete_result = context.performance_monitor.execute_timed_query(query, params)


@when('I attempt to insert the invalid data')
def step_insert_invalid_data(context):
    """Attempt to insert invalid data"""
    try:
        if context.db_manager.db_type == 'mongodb':
            context.invalid_insert_result = context.db_manager.execute_query(
                collection_name='users',
                operation='insert_one',
                document=context.invalid_user_data
            )
        else:
            fields = ', '.join(context.invalid_user_data.keys())
            placeholders = ', '.join([f":{key}" for key in context.invalid_user_data.keys()])
            query = f"INSERT INTO users ({fields}) VALUES ({placeholders})"
            
            context.invalid_insert_result = context.db_manager.execute_query(query, context.invalid_user_data)
    except Exception as e:
        context.validation_error = str(e)


@when('I execute a query to find users by age range')
def step_execute_age_range_query(context):
    """Execute query to find users by age range"""
    if context.db_manager.db_type == 'mongodb':
        context.query_result = context.db_manager.execute_query(
            collection_name='users',
            operation='find',
            query={'age': {'$gte': 20, '$lte': 40}}
        )
    else:
        query = "SELECT * FROM users WHERE age BETWEEN :min_age AND :max_age"
        params = {'min_age': 20, 'max_age': 40}
        
        start_time = time.time()
        context.query_result = context.db_manager.execute_query(query, params)
        context.query_execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds


@then('the user should be successfully created')
def step_verify_user_created(context):
    """Verify user was successfully created"""
    assert context.insert_result['success'], "User insertion failed"


@then('I should be able to retrieve the user by username')
def step_retrieve_user_by_username(context):
    """Retrieve user by username"""
    username = context.user_data['username']
    
    if context.db_manager.db_type == 'mongodb':
        context.retrieved_user = context.db_manager.execute_query(
            collection_name='users',
            operation='find',
            query={'username': username}
        )
        assert context.retrieved_user['success'], "Failed to retrieve user"
        assert len(context.retrieved_user['data']) > 0, "User not found"
        context.retrieved_user_data = context.retrieved_user['data'][0]
    else:
        query = "SELECT * FROM users WHERE username = :username"
        params = {'username': username}
        
        context.retrieved_user = context.db_manager.execute_query(query, params)
        assert context.retrieved_user['success'], "Failed to retrieve user"
        assert len(context.retrieved_user['data']) > 0, "User not found"
        context.retrieved_user_data = context.retrieved_user['data'][0]


@then('the retrieved data should match the inserted data')
def step_verify_retrieved_data_matches(context):
    """Verify retrieved data matches inserted data"""
    for field, value in context.user_data.items():
        assert context.retrieved_user_data[field] == value, \
            f"Field {field}: expected {value}, got {context.retrieved_user_data[field]}"


@then('the user record should be updated successfully')
def step_verify_user_updated(context):
    """Verify user record was updated successfully"""
    assert context.update_result['success'], "User update failed"


@then('the updated fields should have new values')
def step_verify_updated_fields(context):
    """Verify updated fields have new values"""
    username = context.existing_user['username']
    
    if context.db_manager.db_type == 'mongodb':
        result = context.db_manager.execute_query(
            collection_name='users',
            operation='find',
            query={'username': username}
        )
        updated_user = result['data'][0]
    else:
        query = "SELECT * FROM users WHERE username = :username"
        result = context.db_manager.execute_query(query, {'username': username})
        updated_user = result['data'][0]
    
    if hasattr(context, 'new_email'):
        assert updated_user['email'] == context.new_email, "Email was not updated"
    
    if hasattr(context, 'new_age'):
        assert updated_user['age'] == context.new_age, "Age was not updated"


@then('the unchanged fields should remain the same')
def step_verify_unchanged_fields(context):
    """Verify unchanged fields remain the same"""
    # This would check that non-updated fields retain their original values
    pass


@then('the user should be removed successfully')
def step_verify_user_removed(context):
    """Verify user was removed successfully"""
    assert context.delete_result['success'], "User deletion failed"


@then('the user should not be found in subsequent queries')
def step_verify_user_not_found(context):
    """Verify user cannot be found after deletion"""
    if context.db_manager.db_type == 'mongodb':
        result = context.db_manager.execute_query(
            collection_name='users',
            operation='find',
            query={'_id': context.delete_user_id}
        )
        assert len(result['data']) == 0, "Deleted user still found in database"
    else:
        query = "SELECT * FROM users WHERE id = :id"
        result = context.db_manager.execute_query(query, {'id': context.delete_user_id})
        assert len(result['data']) == 0, "Deleted user still found in database"


@then('the database should reject the operation')
def step_verify_operation_rejected(context):
    """Verify database rejected the invalid operation"""
    if hasattr(context, 'invalid_insert_result'):
        assert not context.invalid_insert_result['success'], "Database should have rejected invalid data"
    elif hasattr(context, 'validation_error'):
        assert context.validation_error, "Validation error should have occurred"


@then('an appropriate error should be returned')
def step_verify_appropriate_error(context):
    """Verify appropriate error was returned"""
    if hasattr(context, 'invalid_insert_result') and not context.invalid_insert_result['success']:
        assert 'error' in context.invalid_insert_result, "Error message should be present"
    elif hasattr(context, 'validation_error'):
        assert context.validation_error, "Validation error message should be present"


@then('the query should complete within {max_time:d} milliseconds')
def step_verify_query_performance(context, max_time):
    """Verify query completed within time limit"""
    assert context.query_execution_time < max_time, \
        f"Query took {context.query_execution_time}ms, exceeding limit of {max_time}ms"


@then('the results should be accurate')
def step_verify_results_accurate(context):
    """Verify query results are accurate"""
    assert context.query_result['success'], "Query should be successful"
    
    # Verify all returned users are within the age range
    for user in context.query_result['data']:
        assert 20 <= user['age'] <= 40, f"User age {user['age']} is outside expected range"
