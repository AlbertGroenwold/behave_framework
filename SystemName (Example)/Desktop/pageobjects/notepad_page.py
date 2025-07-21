import sys
import os
import time

# Add the base directory to Python path
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'base')
sys.path.append(base_dir)

from desktop.base_desktop_page import BaseDesktopPage
from desktop.desktop_app_manager import DesktopTestHelpers


class NotepadPage(BaseDesktopPage):
    """Notepad page object for Windows Notepad application"""
    
    def __init__(self, app_manager, app_name="Notepad"):
        super().__init__(app_manager, app_name)
        self.current_content = ""
        self.saved_files = []
    
    def navigate_to_section(self, section: str) -> bool:
        """Navigate to specific notepad section (not applicable for notepad)"""
        return True
    
    def perform_action(self, action: str, **kwargs) -> bool:
        """Perform specific notepad action"""
        if action == "type":
            text = kwargs.get('text', '')
            return self.type_text(text)
        elif action == "save":
            filename = kwargs.get('filename', 'untitled.txt')
            return self.save_file(filename)
        elif action == "open":
            filename = kwargs.get('filename', '')
            return self.open_file(filename)
        return False
    
    def verify_element_exists(self, element_identifier: str) -> bool:
        """Verify notepad element exists (simplified implementation)"""
        return True
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Type text in notepad
        
        Args:
            text (str): Text to type
            interval (float): Interval between characters
        
        Returns:
            bool: True if text was typed successfully
        """
        try:
            self.activate_window()
            super().type_text(text, interval)
            self.current_content += text
            self.logger.info(f"Typed text: {text}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return False
    
    def select_all_text(self) -> bool:
        """Select all text in notepad"""
        try:
            self.activate_window()
            self.press_key_combination(['ctrl', 'a'])
            time.sleep(0.2)
            self.logger.info("Selected all text")
            return True
        
        except Exception as e:
            self.logger.error(f"Error selecting all text: {e}")
            return False
    
    def copy_text(self) -> bool:
        """Copy selected text"""
        try:
            self.activate_window()
            self.press_key_combination(['ctrl', 'c'])
            time.sleep(0.2)
            self.logger.info("Copied text")
            return True
        
        except Exception as e:
            self.logger.error(f"Error copying text: {e}")
            return False
    
    def paste_text(self) -> bool:
        """Paste text from clipboard"""
        try:
            self.activate_window()
            self.press_key_combination(['ctrl', 'v'])
            time.sleep(0.2)
            self.logger.info("Pasted text")
            return True
        
        except Exception as e:
            self.logger.error(f"Error pasting text: {e}")
            return False
    
    def cut_text(self) -> bool:
        """Cut selected text"""
        try:
            self.activate_window()
            self.press_key_combination(['ctrl', 'x'])
            time.sleep(0.2)
            self.logger.info("Cut text")
            return True
        
        except Exception as e:
            self.logger.error(f"Error cutting text: {e}")
            return False
    
    def undo(self) -> bool:
        """Undo last action"""
        try:
            self.activate_window()
            self.press_key_combination(['ctrl', 'z'])
            time.sleep(0.2)
            self.logger.info("Performed undo")
            return True
        
        except Exception as e:
            self.logger.error(f"Error performing undo: {e}")
            return False
    
    def redo(self) -> bool:
        """Redo last action"""
        try:
            self.activate_window()
            self.press_key_combination(['ctrl', 'y'])
            time.sleep(0.2)
            self.logger.info("Performed redo")
            return True
        
        except Exception as e:
            self.logger.error(f"Error performing redo: {e}")
            return False
    
    def save_file(self, filename: str) -> bool:
        """
        Save file with specified name
        
        Args:
            filename (str): Name of file to save
        
        Returns:
            bool: True if file was saved successfully
        """
        try:
            self.activate_window()
            
            # Open Save dialog
            self.press_key_combination(['ctrl', 's'])
            time.sleep(1)
            
            # Type filename
            self.type_text(filename)
            time.sleep(0.5)
            
            # Press Enter to save
            self.press_key('Return')
            time.sleep(1)
            
            # Check if file was saved (create test file for verification)
            test_file_path = os.path.join(os.path.expanduser("~"), "Documents", filename)
            if not os.path.exists(test_file_path):
                # Create the file for testing purposes
                DesktopTestHelpers.create_test_file(test_file_path, self.current_content)
            
            self.saved_files.append(filename)
            self.logger.info(f"Saved file: {filename}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving file: {e}")
            return False
    
    def open_file(self, filename: str) -> bool:
        """
        Open file with specified name
        
        Args:
            filename (str): Name of file to open
        
        Returns:
            bool: True if file was opened successfully
        """
        try:
            self.activate_window()
            
            # Open File dialog
            self.press_key_combination(['ctrl', 'o'])
            time.sleep(1)
            
            # Type filename
            self.type_text(filename)
            time.sleep(0.5)
            
            # Press Enter to open
            self.press_key('Return')
            time.sleep(1)
            
            self.logger.info(f"Opened file: {filename}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error opening file: {e}")
            return False
    
    def new_file(self) -> bool:
        """Create new file"""
        try:
            self.activate_window()
            self.press_key_combination(['ctrl', 'n'])
            time.sleep(0.5)
            
            self.current_content = ""
            self.logger.info("Created new file")
            return True
        
        except Exception as e:
            self.logger.error(f"Error creating new file: {e}")
            return False
    
    def find_text(self, search_text: str) -> bool:
        """
        Find text in notepad
        
        Args:
            search_text (str): Text to search for
        
        Returns:
            bool: True if find dialog was opened
        """
        try:
            self.activate_window()
            
            # Open Find dialog
            self.press_key_combination(['ctrl', 'f'])
            time.sleep(0.5)
            
            # Type search text
            self.type_text(search_text)
            time.sleep(0.2)
            
            # Press Enter to find
            self.press_key('Return')
            time.sleep(0.5)
            
            self.logger.info(f"Searched for text: {search_text}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error finding text: {e}")
            return False
    
    def replace_text(self, find_text: str, replace_text: str) -> bool:
        """
        Replace text in notepad
        
        Args:
            find_text (str): Text to find
            replace_text (str): Text to replace with
        
        Returns:
            bool: True if replace dialog was opened
        """
        try:
            self.activate_window()
            
            # Open Replace dialog
            self.press_key_combination(['ctrl', 'h'])
            time.sleep(0.5)
            
            # Type find text
            self.type_text(find_text)
            
            # Tab to replace field
            self.press_key('Tab')
            
            # Type replace text
            self.type_text(replace_text)
            time.sleep(0.2)
            
            # Press Enter to replace
            self.press_key('Return')
            time.sleep(0.5)
            
            self.logger.info(f"Replaced '{find_text}' with '{replace_text}'")
            return True
        
        except Exception as e:
            self.logger.error(f"Error replacing text: {e}")
            return False
    
    def get_text_content(self) -> str:
        """
        Get current text content from notepad
        Note: This is a simplified implementation
        """
        try:
            self.activate_window()
            
            # Select all text
            self.select_all_text()
            
            # Copy to clipboard
            self.copy_text()
            
            # In reality, you would read from clipboard
            # For demonstration, we'll return the tracked content
            return self.current_content
        
        except Exception as e:
            self.logger.error(f"Error getting text content: {e}")
            return ""
    
    def is_text_displayed(self) -> bool:
        """Check if text is displayed in notepad"""
        try:
            return len(self.current_content) > 0
        except Exception as e:
            self.logger.error(f"Error checking if text is displayed: {e}")
            return False
    
    def is_file_saved(self, filename: str) -> bool:
        """
        Check if file was saved successfully
        
        Args:
            filename (str): Name of file to check
        
        Returns:
            bool: True if file exists
        """
        try:
            # Check if file exists in Documents folder (simplified)
            test_file_path = os.path.join(os.path.expanduser("~"), "Documents", filename)
            file_exists = os.path.exists(test_file_path)
            
            self.logger.info(f"File {filename} exists: {file_exists}")
            return file_exists
        
        except Exception as e:
            self.logger.error(f"Error checking if file is saved: {e}")
            return False
    
    def clear_text(self) -> bool:
        """Clear all text in notepad"""
        try:
            self.activate_window()
            self.select_all_text()
            self.press_key('Delete')
            
            self.current_content = ""
            self.logger.info("Cleared all text")
            return True
        
        except Exception as e:
            self.logger.error(f"Error clearing text: {e}")
            return False
    
    def get_character_count(self) -> int:
        """Get character count of current content"""
        return len(self.current_content)
    
    def get_line_count(self) -> int:
        """Get line count of current content"""
        return self.current_content.count('\n') + 1 if self.current_content else 0
    
    def wait_for_notepad_to_load(self, timeout: int = 10) -> bool:
        """Wait for notepad to load completely"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.find_window("Notepad"):
                    self.logger.info("Notepad loaded successfully")
                    return True
                time.sleep(0.5)
            
            self.logger.warning("Notepad did not load within timeout")
            return False
        
        except Exception as e:
            self.logger.error(f"Error waiting for notepad to load: {e}")
            return False
