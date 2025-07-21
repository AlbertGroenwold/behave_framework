from behave import given, when, then
import sys
import os
import time

# Add the base directory to Python path
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from desktop.base_desktop_page import BaseDesktopPage
from desktop.desktop_app_manager import DesktopAppManager


@given('I have desktop applications available')
def step_desktop_apps_available(context):
    """Verify desktop applications are available"""
    if not hasattr(context, 'app_manager'):
        context.app_manager = DesktopAppManager('config/desktop_config.ini')
    
    # Verify system is ready for desktop testing
    system_info = context.app_manager.get_system_info()
    assert system_info['system'] == 'Windows', "Desktop testing requires Windows OS"


@given('I launch the calculator application')
def step_launch_calculator(context):
    """Launch calculator application"""
    if not hasattr(context, 'app_manager'):
        context.app_manager = DesktopAppManager('config/desktop_config.ini')
    
    # Launch Windows Calculator
    calc_path = "calc.exe"
    result = context.app_manager.launch_application(calc_path, "Calculator")
    assert result['success'], f"Failed to launch calculator: {result.get('error', '')}"
    
    # Initialize calculator page object
    from CentralQualityHub.Desktop.pageobjects.calculator_page import CalculatorPage
    context.calculator_page = CalculatorPage(context.app_manager, "Calculator")
    
    # Wait for calculator to load
    time.sleep(2)
    assert context.calculator_page.find_window("Calculator"), "Calculator window not found"


@given('I launch the notepad application')
def step_launch_notepad(context):
    """Launch notepad application"""
    if not hasattr(context, 'app_manager'):
        context.app_manager = DesktopAppManager('config/desktop_config.ini')
    
    # Launch Windows Notepad
    notepad_path = "notepad.exe"
    result = context.app_manager.launch_application(notepad_path, "Notepad")
    assert result['success'], f"Failed to launch notepad: {result.get('error', '')}"
    
    # Initialize notepad page object
    from CentralQualityHub.Desktop.pageobjects.notepad_page import NotepadPage
    context.notepad_page = NotepadPage(context.app_manager, "Notepad")
    
    # Wait for notepad to load
    time.sleep(2)
    assert context.notepad_page.find_window("Notepad"), "Notepad window not found"


@when('I perform the calculation "{calculation}"')
def step_perform_calculation(context, calculation):
    """Perform calculation in calculator"""
    context.calculator_page.activate_window()
    context.calculator_page.perform_calculation(calculation)


@when('I clear the calculator')
def step_clear_calculator(context):
    """Clear calculator display"""
    context.calculator_page.clear_calculator()


@when('I enter the numbers and operations')
def step_enter_numbers_and_operations(context):
    """Enter numbers and operations from table"""
    for row in context.table:
        operation = row['operation']
        value = row['value']
        
        if operation == 'number':
            context.calculator_page.enter_number(value)
        elif operation == 'add':
            context.calculator_page.click_add()
            context.calculator_page.enter_number(value)
        elif operation == 'subtract':
            context.calculator_page.click_subtract()
            context.calculator_page.enter_number(value)
        elif operation == 'multiply':
            context.calculator_page.click_multiply()
            context.calculator_page.enter_number(value)
        elif operation == 'divide':
            context.calculator_page.click_divide()
            context.calculator_page.enter_number(value)
        elif operation == 'equals':
            context.calculator_page.click_equals()


@when('I type the text "{text}"')
def step_type_text(context, text):
    """Type text in notepad"""
    context.notepad_page.activate_window()
    context.notepad_page.type_text(text)


@when('I select all text')
def step_select_all_text(context):
    """Select all text in notepad"""
    context.notepad_page.select_all_text()


@when('I copy the text')
def step_copy_text(context):
    """Copy text in notepad"""
    context.notepad_page.copy_text()


@when('I paste the text')
def step_paste_text(context):
    """Paste text in notepad"""
    context.notepad_page.paste_text()


@when('I save the file as "{filename}"')
def step_save_file(context, filename):
    """Save file in notepad"""
    context.notepad_page.save_file(filename)
    context.saved_filename = filename


@when('I open the file "{filename}"')
def step_open_file(context, filename):
    """Open file in notepad"""
    context.notepad_page.open_file(filename)


@when('I maximize the window')
def step_maximize_window(context):
    """Maximize calculator window"""
    context.calculator_page.maximize_window()


@when('I minimize the window')
def step_minimize_window(context):
    """Minimize calculator window"""
    context.calculator_page.minimize_window()


@when('I restore the window')
def step_restore_window(context):
    """Restore calculator window"""
    context.calculator_page.activate_window()


@when('I move the window to position "{position}"')
def step_move_window(context, position):
    """Move window to specified position"""
    x, y = map(int, position.split(', '))
    context.calculator_page.move_window(x, y)
    context.target_position = (x, y)


@when('I take a screenshot of the calculator')
def step_take_calculator_screenshot(context):
    """Take screenshot of calculator"""
    context.calculator_page.activate_window()
    context.screenshot_path = context.calculator_page.take_screenshot("calculator_screenshot.png")


@when('I click on the number "{number}" button')
def step_click_number_button(context, number):
    """Click number button in calculator"""
    context.calculator_page.click_number(number)


@when('I take a screenshot of the display')
def step_take_display_screenshot(context):
    """Take screenshot of calculator display"""
    context.display_screenshot = context.calculator_page.take_screenshot("calculator_display.png")


@when('I press "{key_combination}" to {action}')
def step_press_key_combination(context, key_combination, action):
    """Press key combination"""
    if key_combination == "Ctrl+A":
        context.notepad_page.press_key_combination(['ctrl', 'a'])
    elif key_combination == "Ctrl+C":
        context.notepad_page.press_key_combination(['ctrl', 'c'])
    elif key_combination == "Ctrl+V":
        context.notepad_page.press_key_combination(['ctrl', 'v'])


@when('I switch between applications')
def step_switch_between_applications(context):
    """Switch between applications"""
    # Switch to calculator
    context.calculator_page.activate_window()
    time.sleep(1)
    
    # Switch to notepad
    context.notepad_page.activate_window()
    time.sleep(1)


@when('I perform operations in each application')
def step_perform_operations_in_each_app(context):
    """Perform operations in each application"""
    # Perform calculation in calculator
    context.calculator_page.activate_window()
    context.calculator_page.perform_calculation("2 + 2")
    
    # Type text in notepad
    context.notepad_page.activate_window()
    context.notepad_page.type_text("Multi-app test")


@then('the result should be "{expected_result}"')
def step_verify_result(context, expected_result):
    """Verify calculation result"""
    actual_result = context.calculator_page.get_display_value()
    assert actual_result == expected_result, f"Expected {expected_result}, got {actual_result}"


@then('the text should be displayed in the notepad')
def step_verify_text_displayed(context):
    """Verify text is displayed in notepad"""
    assert context.notepad_page.is_text_displayed(), "Text is not displayed in notepad"


@then('the notepad should contain "{expected_text}"')
def step_verify_notepad_contains_text(context, expected_text):
    """Verify notepad contains expected text"""
    actual_text = context.notepad_page.get_text_content()
    assert expected_text in actual_text, f"Expected text '{expected_text}' not found in '{actual_text}'"


@then('the file should be saved successfully')
def step_verify_file_saved(context):
    """Verify file was saved successfully"""
    # Check if file exists (implementation depends on file system check)
    assert context.notepad_page.is_file_saved(context.saved_filename), "File was not saved successfully"


@then('the file content should be "{expected_content}"')
def step_verify_file_content(context, expected_content):
    """Verify file content matches expected"""
    actual_content = context.notepad_page.get_text_content()
    assert expected_content in actual_content, f"Expected content not found. Got: {actual_content}"


@then('the calculator window should be maximized')
def step_verify_window_maximized(context):
    """Verify calculator window is maximized"""
    # Implementation would check window state
    assert context.calculator_page.is_window_maximized(), "Calculator window is not maximized"


@then('the calculator window should be minimized')
def step_verify_window_minimized(context):
    """Verify calculator window is minimized"""
    assert context.calculator_page.is_window_minimized(), "Calculator window is not minimized"


@then('the calculator window should be restored')
def step_verify_window_restored(context):
    """Verify calculator window is restored"""
    assert context.calculator_page.is_window_restored(), "Calculator window is not restored"


@then('the calculator window should be at position "{expected_position}"')
def step_verify_window_position(context, expected_position):
    """Verify calculator window position"""
    x, y, width, height = context.calculator_page.get_window_position()
    expected_x, expected_y = map(int, expected_position.split(', '))
    
    # Allow some tolerance for window positioning
    tolerance = 10
    assert abs(x - expected_x) <= tolerance and abs(y - expected_y) <= tolerance, \
        f"Window position ({x}, {y}) doesn't match expected ({expected_x}, {expected_y})"


@then('the screenshot should be saved successfully')
def step_verify_screenshot_saved(context):
    """Verify screenshot was saved successfully"""
    assert context.screenshot_path, "Screenshot path is empty"
    assert os.path.exists(context.screenshot_path), "Screenshot file was not created"


@then('the display should show "{expected_value}"')
def step_verify_display_value(context, expected_value):
    """Verify calculator display shows expected value"""
    actual_value = context.calculator_page.get_display_value()
    assert actual_value == expected_value, f"Display shows '{actual_value}', expected '{expected_value}'"


@then('the notepad should contain the duplicated text')
def step_verify_duplicated_text(context):
    """Verify notepad contains duplicated text"""
    text_content = context.notepad_page.get_text_content()
    # The text should appear twice due to copy-paste operation
    assert text_content.count("Test content for shortcuts") >= 2, "Text was not duplicated properly"


@then('both applications should maintain their state')
def step_verify_applications_maintain_state(context):
    """Verify both applications maintain their state"""
    # Check calculator state
    context.calculator_page.activate_window()
    calc_result = context.calculator_page.get_display_value()
    assert calc_result == "4", f"Calculator state not maintained. Expected 4, got {calc_result}"
    
    # Check notepad state
    context.notepad_page.activate_window()
    notepad_content = context.notepad_page.get_text_content()
    assert "Multi-app test" in notepad_content, "Notepad state not maintained"


@then('I should be able to interact with both')
def step_verify_can_interact_with_both(context):
    """Verify can interact with both applications"""
    # Test calculator interaction
    context.calculator_page.activate_window()
    context.calculator_page.click_number("1")
    
    # Test notepad interaction
    context.notepad_page.activate_window()
    context.notepad_page.type_text(" - additional text")
    
    # Both interactions should be successful (no assertions needed as exceptions would be raised)
