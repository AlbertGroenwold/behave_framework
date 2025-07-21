import time
import logging
from datetime import datetime, timedelta


class DateTimeUtils:
    """Utility class for date and time operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_current_timestamp(self, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Get current timestamp as string
        
        Args:
            format_string (str): Date format string
        
        Returns:
            str: Formatted timestamp
        """
        try:
            timestamp = datetime.now().strftime(format_string)
            self.logger.info(f"Current timestamp: {timestamp}")
            return timestamp
        
        except Exception as e:
            self.logger.error(f"Error getting current timestamp: {e}")
            raise
    
    def get_future_date(self, days: int = 1, format_string: str = "%Y-%m-%d") -> str:
        """
        Get future date
        
        Args:
            days (int): Number of days in the future
            format_string (str): Date format string
        
        Returns:
            str: Formatted future date
        """
        try:
            future_date = datetime.now() + timedelta(days=days)
            formatted_date = future_date.strftime(format_string)
            self.logger.info(f"Future date (+{days} days): {formatted_date}")
            return formatted_date
        
        except Exception as e:
            self.logger.error(f"Error getting future date: {e}")
            raise
    
    def get_past_date(self, days: int = 1, format_string: str = "%Y-%m-%d") -> str:
        """
        Get past date
        
        Args:
            days (int): Number of days in the past
            format_string (str): Date format string
        
        Returns:
            str: Formatted past date
        """
        try:
            past_date = datetime.now() - timedelta(days=days)
            formatted_date = past_date.strftime(format_string)
            self.logger.info(f"Past date (-{days} days): {formatted_date}")
            return formatted_date
        
        except Exception as e:
            self.logger.error(f"Error getting past date: {e}")
            raise
    
    def parse_date(self, date_string: str, format_string: str = "%Y-%m-%d") -> datetime:
        """
        Parse date string to datetime object
        
        Args:
            date_string (str): Date string to parse
            format_string (str): Expected date format
        
        Returns:
            datetime: Parsed datetime object
        """
        try:
            parsed_date = datetime.strptime(date_string, format_string)
            self.logger.info(f"Parsed date: {date_string} -> {parsed_date}")
            return parsed_date
        
        except Exception as e:
            self.logger.error(f"Error parsing date {date_string}: {e}")
            raise
    
    def format_date(self, date_obj: datetime, format_string: str = "%Y-%m-%d") -> str:
        """
        Format datetime object to string
        
        Args:
            date_obj (datetime): Datetime object
            format_string (str): Desired format
        
        Returns:
            str: Formatted date string
        """
        try:
            formatted = date_obj.strftime(format_string)
            self.logger.info(f"Formatted date: {date_obj} -> {formatted}")
            return formatted
        
        except Exception as e:
            self.logger.error(f"Error formatting date: {e}")
            raise
    
    def wait_for_seconds(self, seconds: float) -> None:
        """
        Wait for specified number of seconds
        
        Args:
            seconds (float): Number of seconds to wait
        """
        try:
            self.logger.info(f"Waiting for {seconds} seconds...")
            time.sleep(seconds)
            self.logger.info("Wait completed")
        
        except Exception as e:
            self.logger.error(f"Error during wait: {e}")
            raise
