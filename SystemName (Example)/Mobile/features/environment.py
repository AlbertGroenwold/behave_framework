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
    print("CENTRAL QUALITY HUB - MOBILE AUTOMATION TESTING")
    print("=" * 80)


def before_scenario(context, scenario):
    """Setup before each scenario"""
    # Initialize mobile driver for mobile scenarios
    if any(tag in scenario.tags for tag in ['mobile', 'android', 'ios']):
        from mobile.mobile_driver_manager import MobileDriverManager
        
        platform = 'android' if 'android' in scenario.tags else 'ios'
        
        context.mobile_driver_manager = MobileDriverManager('config/mobile_config.ini')
        context.driver = context.mobile_driver_manager.start_driver(platform)
        
        print(f"\n📱 Starting Mobile Scenario: {scenario.name}")
        print(f"Platform: {platform.upper()}")


def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    # Close mobile driver for mobile scenarios
    if hasattr(context, 'driver'):
        try:
            context.mobile_driver_manager.stop_driver()
            print(f"✅ Mobile Scenario completed: {scenario.name}")
        except Exception as e:
            print(f"⚠️ Error closing mobile driver: {e}")
        finally:
            if hasattr(context, 'mobile_driver_manager'):
                delattr(context, 'mobile_driver_manager')
            delattr(context, 'driver')
    
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
    print("MOBILE AUTOMATION TEST SUMMARY")
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
