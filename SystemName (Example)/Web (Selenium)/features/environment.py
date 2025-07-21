import sys
import os
from pathlib import Path

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
    print("CENTRAL QUALITY HUB - WEB AUTOMATION TESTING")
    print("=" * 80)


def before_scenario(context, scenario):
    """Setup before each scenario"""
    # Initialize web driver for web scenarios
    if any(tag in scenario.tags for tag in ['web', 'login', 'user_management']):
        from web.webdriver_manager import WebDriverManager
        
        browser = getattr(context, 'browser', 'chrome')
        headless = getattr(context, 'headless', False)
        
        context.driver_manager = WebDriverManager()
        context.driver = context.driver_manager.get_driver(browser, headless=headless)
        
        print(f"\n📱 Starting Web Scenario: {scenario.name}")
        print(f"Browser: {browser.upper()}")


def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    # Close web driver for web scenarios
    if hasattr(context, 'driver'):
        try:
            context.driver.quit()
            print(f"✅ Web Scenario completed: {scenario.name}")
        except Exception as e:
            print(f"⚠️ Error closing driver: {e}")
        finally:
            delattr(context, 'driver')
            if hasattr(context, 'driver_manager'):
                delattr(context, 'driver_manager')
    
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
    print("WEB AUTOMATION TEST SUMMARY")
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
