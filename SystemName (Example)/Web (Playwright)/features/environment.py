import sys
import os
from pathlib import Path

def before_all(context):
    """Setup before all scenarios"""
    # Add base directory to Python path
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
    if base_dir not in sys.path:
        sys.path.append(base_dir)
    
    # Set up context attributes
    context.test_results = []
    context.failed_scenarios = []
    
    print("=" * 80)
    print("CENTRAL QUALITY HUB - WEB AUTOMATION TESTING (PLAYWRIGHT)")
    print("=" * 80)


def before_scenario(context, scenario):
    """Setup before each scenario"""
    # Initialize Playwright for web scenarios
    if any(tag in scenario.tags for tag in ['web', 'playwright', 'login', 'user_management']):
        from web_playwright.playwright_manager import PlaywrightManager
        
        browser = getattr(context, 'browser', 'chromium')
        headless = getattr(context, 'headless', False)
        
        context.playwright_manager = PlaywrightManager()
        context.playwright_manager.start_playwright()
        context.playwright_manager.launch_browser(browser_name=browser, headless=headless)
        context.playwright_manager.create_context()
        context.playwright_manager.create_page()
        
        # Set default timeouts
        context.playwright_manager.page.set_default_timeout(30000)
        
        print(f"\n🎭 Starting Playwright Scenario: {scenario.name}")
        print(f"Browser: {browser.upper()}")


def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    # Close Playwright resources for web scenarios
    if hasattr(context, 'playwright_manager'):
        try:
            # Take screenshot on failure
            if scenario.status == 'failed':
                screenshot_dir = os.path.join(os.path.dirname(__file__), '..', 'screenshots')
                os.makedirs(screenshot_dir, exist_ok=True)
                screenshot_path = os.path.join(screenshot_dir, f"{scenario.name}_{context.playwright_manager.get_timestamp()}.png")
                context.playwright_manager.page.screenshot(path=screenshot_path)
                print(f"📸 Screenshot saved: {screenshot_path}")
            
            context.playwright_manager.close_all()
            print(f"✅ Playwright Scenario completed: {scenario.name}")
        except Exception as e:
            print(f"⚠️ Error closing Playwright: {e}")
        finally:
            if hasattr(context, 'playwright_manager'):
                delattr(context, 'playwright_manager')
    
    # Record test results
    context.test_results.append({
        'scenario': scenario.name,
        'status': scenario.status,
        'tags': scenario.tags
    })
    
    if scenario.status == 'failed':
        context.failed_scenarios.append(scenario.name)


def after_all(context):
    """Cleanup after all scenarios"""
    # Print test summary
    total_scenarios = len(context.test_results)
    passed_scenarios = len([r for r in context.test_results if r['status'] == 'passed'])
    failed_scenarios = len(context.failed_scenarios)
    
    print("\n" + "=" * 80)
    print("PLAYWRIGHT TEST EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total Scenarios: {total_scenarios}")
    print(f"Passed: {passed_scenarios}")
    print(f"Failed: {failed_scenarios}")
    
    if context.failed_scenarios:
        print("\nFailed Scenarios:")
        for failed_scenario in context.failed_scenarios:
            print(f"  ❌ {failed_scenario}")
    
    print("=" * 80)


def before_feature(context, feature):
    """Setup before each feature"""
    print(f"\n🚀 Starting Feature: {feature.name}")
    if feature.description:
        for line in feature.description:
            print(f"   {line}")


def after_feature(context, feature):
    """Cleanup after each feature"""
    print(f"✅ Feature completed: {feature.name}")


def before_step(context, step):
    """Setup before each step"""
    print(f"  📝 {step.step_type.title()}: {step.name}")


def after_step(context, step):
    """Cleanup after each step"""
    if step.status == 'failed':
        print(f"  ❌ Step failed: {step.name}")
        # You can add additional error logging here
    elif step.status == 'passed':
        print(f"  ✅ Step passed: {step.name}")
