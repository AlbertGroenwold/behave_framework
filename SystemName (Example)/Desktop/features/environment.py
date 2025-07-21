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
    
    print("=" * 80)
    print("CENTRAL QUALITY HUB - DESKTOP AUTOMATION TESTING")
    print("=" * 80)


def before_scenario(context, scenario):
    """Setup before each scenario"""
    print(f"\n🖥️ Starting Desktop Scenario: {scenario.name}")


def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    # Close desktop applications
    if hasattr(context, 'app_manager'):
        try:
            context.app_manager.cleanup_all_managed_applications()
            print(f"✅ Desktop Scenario completed: {scenario.name}")
        except Exception as e:
            print(f"⚠️ Error closing desktop applications: {e}")
    
    # Clean up test files
    if hasattr(context, 'saved_filename'):
        try:
            test_file_path = os.path.join(os.path.expanduser("~"), "Documents", context.saved_filename)
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
        except Exception as e:
            print(f"⚠️ Error cleaning up test file: {e}")
    
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
    # Final cleanup of any remaining applications
    if hasattr(context, 'app_manager'):
        context.app_manager.cleanup_all_managed_applications()
    
    print("\n" + "=" * 80)
    print("DESKTOP AUTOMATION TEST SUMMARY")
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
