import random
import string
import logging
import uuid
import re
from typing import List


class StringUtils:
    """Utility class for string operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_random_string(self, length: int = 10, 
                             include_uppercase: bool = True,
                             include_lowercase: bool = True,
                             include_digits: bool = True,
                             include_special: bool = False,
                             special_chars: str = "!@#$%^&*()") -> str:
        """
        Generate random string
        
        Args:
            length (int): String length
            include_uppercase (bool): Include uppercase letters
            include_lowercase (bool): Include lowercase letters
            include_digits (bool): Include digits
            include_special (bool): Include special characters
            special_chars (str): Special characters to include
        
        Returns:
            str: Random string
        """
        try:
            characters = ""
            
            if include_uppercase:
                characters += string.ascii_uppercase
            if include_lowercase:
                characters += string.ascii_lowercase
            if include_digits:
                characters += string.digits
            if include_special:
                characters += special_chars
            
            if not characters:
                raise ValueError("At least one character type must be included")
            
            random_string = ''.join(random.choice(characters) for _ in range(length))
            
            self.logger.info(f"Generated random string of length {length}")
            return random_string
        
        except Exception as e:
            self.logger.error(f"Error generating random string: {e}")
            raise
    
    def generate_random_email(self, domain: str = "example.com") -> str:
        """
        Generate random email address
        
        Args:
            domain (str): Email domain
        
        Returns:
            str: Random email address
        """
        try:
            username = self.generate_random_string(
                length=random.randint(5, 10),
                include_uppercase=False,
                include_special=False
            )
            email = f"{username}@{domain}"
            
            self.logger.info(f"Generated random email: {email}")
            return email
        
        except Exception as e:
            self.logger.error(f"Error generating random email: {e}")
            raise
    
    def generate_uuid(self, version: int = 4) -> str:
        """
        Generate UUID
        
        Args:
            version (int): UUID version (1 or 4)
        
        Returns:
            str: UUID string
        """
        try:
            if version == 1:
                generated_uuid = str(uuid.uuid1())
            elif version == 4:
                generated_uuid = str(uuid.uuid4())
            else:
                raise ValueError("Supported UUID versions: 1, 4")
            
            self.logger.info(f"Generated UUID v{version}: {generated_uuid}")
            return generated_uuid
        
        except Exception as e:
            self.logger.error(f"Error generating UUID: {e}")
            raise
    
    def clean_string(self, text: str, remove_extra_spaces: bool = True,
                    remove_special_chars: bool = False,
                    allowed_special_chars: str = "") -> str:
        """
        Clean and normalize string
        
        Args:
            text (str): Text to clean
            remove_extra_spaces (bool): Remove extra spaces
            remove_special_chars (bool): Remove special characters
            allowed_special_chars (str): Special characters to keep
        
        Returns:
            str: Cleaned string
        """
        try:
            cleaned = text.strip()
            
            if remove_extra_spaces:
                cleaned = re.sub(r'\s+', ' ', cleaned)
            
            if remove_special_chars:
                if allowed_special_chars:
                    pattern = f"[^a-zA-Z0-9\\s{re.escape(allowed_special_chars)}]"
                else:
                    pattern = r"[^a-zA-Z0-9\s]"
                cleaned = re.sub(pattern, '', cleaned)
            
            self.logger.info("String cleaned successfully")
            return cleaned
        
        except Exception as e:
            self.logger.error(f"Error cleaning string: {e}")
            raise
    
    def mask_sensitive_data(self, text: str, mask_char: str = "*", 
                          show_first: int = 2, show_last: int = 2) -> str:
        """
        Mask sensitive data in string
        
        Args:
            text (str): Text to mask
            mask_char (str): Character to use for masking
            show_first (int): Number of characters to show at start
            show_last (int): Number of characters to show at end
        
        Returns:
            str: Masked string
        """
        try:
            if len(text) <= (show_first + show_last):
                return mask_char * len(text)
            
            masked_length = len(text) - show_first - show_last
            masked = (text[:show_first] + 
                     mask_char * masked_length + 
                     text[-show_last:])
            
            self.logger.info("Sensitive data masked")
            return masked
        
        except Exception as e:
            self.logger.error(f"Error masking sensitive data: {e}")
            raise
    
    def extract_numbers(self, text: str) -> List[str]:
        """
        Extract numbers from string
        
        Args:
            text (str): Text to extract numbers from
        
        Returns:
            List[str]: List of numbers found
        """
        try:
            numbers = re.findall(r'\d+\.?\d*', text)
            self.logger.info(f"Extracted {len(numbers)} numbers from text")
            return numbers
        
        except Exception as e:
            self.logger.error(f"Error extracting numbers: {e}")
            raise
    
    def extract_emails(self, text: str) -> List[str]:
        """
        Extract email addresses from string
        
        Args:
            text (str): Text to extract emails from
        
        Returns:
            List[str]: List of email addresses found
        """
        try:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            self.logger.info(f"Extracted {len(emails)} email addresses from text")
            return emails
        
        except Exception as e:
            self.logger.error(f"Error extracting emails: {e}")
            raise
    
    def extract_urls(self, text: str) -> List[str]:
        """
        Extract URLs from string
        
        Args:
            text (str): Text to extract URLs from
        
        Returns:
            List[str]: List of URLs found
        """
        try:
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, text)
            self.logger.info(f"Extracted {len(urls)} URLs from text")
            return urls
        
        except Exception as e:
            self.logger.error(f"Error extracting URLs: {e}")
            raise
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email address format
        
        Args:
            email (str): Email address to validate
        
        Returns:
            bool: True if valid
        """
        try:
            email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
            is_valid = bool(re.match(email_pattern, email))
            self.logger.info(f"Email validation for {email}: {is_valid}")
            return is_valid
        
        except Exception as e:
            self.logger.error(f"Error validating email: {e}")
            return False
    
    def validate_phone(self, phone: str, country_code: str = "US") -> bool:
        """
        Validate phone number format
        
        Args:
            phone (str): Phone number to validate
            country_code (str): Country code for validation
        
        Returns:
            bool: True if valid
        """
        try:
            # Remove all non-digit characters
            digits_only = re.sub(r'\D', '', phone)
            
            if country_code == "US":
                # US phone number: 10 digits
                is_valid = len(digits_only) == 10
            else:
                # Basic validation for international numbers
                is_valid = 7 <= len(digits_only) <= 15
            
            self.logger.info(f"Phone validation for {phone}: {is_valid}")
            return is_valid
        
        except Exception as e:
            self.logger.error(f"Error validating phone: {e}")
            return False
