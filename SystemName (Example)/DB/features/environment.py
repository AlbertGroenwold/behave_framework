import sys
import os

def before_all(context):
    """Setup before all scenarios"""
    # Add base directory to Python path
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'base')
    if base_dir not in sys.path:
        sys.path.append(base_dir)
    
    # Set up context attributes
    context.test_results = []
    context.failed_scenarios = []
    
    # Set default database type (can be overridden)
    context.db_type = getattr(context, 'db_type', 'postgresql')
    
    print("=" * 80)
    print("CENTRAL QUALITY HUB - DATABASE AUTOMATION TESTING")
    print(f"Database Type: {context.db_type.upper()}")
    print("=" * 80)


def before_scenario(context, scenario):
    """Setup before each scenario"""
    print(f"\n🗄️ Starting Database Scenario: {scenario.name}")


def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    # Clean up database connections
    if hasattr(context, 'db_manager'):
        try:
            context.db_manager.disconnect()
        except Exception as e:
            print(f"⚠️ Error disconnecting from database: {e}")
    
    # Clean up test data if needed
    if hasattr(context, 'created_user_id') and hasattr(context, 'db_manager'):
        try:
            # Clean up created test data
            if context.db_manager.db_type == 'mongodb':
                context.db_manager.execute_query(
                    collection_name='users',
                    operation='delete_one',
                    query={'_id': context.created_user_id}
                )
            else:
                context.db_manager.execute_query(
                    "DELETE FROM users WHERE id = :id",
                    {'id': context.created_user_id}
                )
        except Exception as e:
            print(f"⚠️ Error cleaning up test data: {e}")
    
    # Record scenario results
    if scenario.status == "failed":
        context.failed_scenarios.append(scenario.name)
        print(f"❌ Scenario FAILED: {scenario.name}")
    else:
        print(f"✅ Scenario PASSED: {scenario.name}")
    
    context.test_results.append({
        'scenario': scenario.name,
        'status': scenario.status,
        'tags': list(scenario.tags)
    })


def after_all(context):
    """Cleanup after all scenarios"""
    print("\n" + "=" * 80)
    print("DATABASE AUTOMATION TEST SUMMARY")
    print("=" * 80)
    
    total_scenarios = len(context.test_results)
    passed_scenarios = len([r for r in context.test_results if r['status'] == 'passed'])
    failed_scenarios = len([r for r in context.test_results if r['status'] == 'failed'])
    
    print(f"Total Scenarios: {total_scenarios}")
    print(f"Passed: {passed_scenarios}")
    print(f"Failed: {failed_scenarios}")
    
    if failed_scenarios > 0:
        print(f"\nFailed Scenarios:")
        for scenario in context.failed_scenarios:
            print(f"  - {scenario}")
    
    print("=" * 80)
