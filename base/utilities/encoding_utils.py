import base64
import hashlib
import logging


class EncodingUtils:
    """Utility class for encoding/decoding operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def encode_base64(self, text: str, encoding: str = 'utf-8') -> str:
        """
        Encode string to Base64
        
        Args:
            text (str): Text to encode
            encoding (str): Text encoding
        
        Returns:
            str: Base64 encoded string
        """
        try:
            encoded_bytes = base64.b64encode(text.encode(encoding))
            encoded_string = encoded_bytes.decode('ascii')
            self.logger.info("String encoded to Base64")
            return encoded_string
        
        except Exception as e:
            self.logger.error(f"Error encoding to Base64: {e}")
            raise
    
    def decode_base64(self, encoded_text: str, encoding: str = 'utf-8') -> str:
        """
        Decode Base64 string
        
        Args:
            encoded_text (str): Base64 encoded text
            encoding (str): Target encoding
        
        Returns:
            str: Decoded string
        """
        try:
            decoded_bytes = base64.b64decode(encoded_text)
            decoded_string = decoded_bytes.decode(encoding)
            self.logger.info("Base64 string decoded")
            return decoded_string
        
        except Exception as e:
            self.logger.error(f"Error decoding from Base64: {e}")
            raise
    
    def calculate_hash(self, text: str, algorithm: str = 'md5', encoding: str = 'utf-8') -> str:
        """
        Calculate hash of string
        
        Args:
            text (str): Text to hash
            algorithm (str): Hash algorithm (md5, sha1, sha256, sha512)
            encoding (str): Text encoding
        
        Returns:
            str: Hash string
        """
        try:
            hash_obj = hashlib.new(algorithm)
            hash_obj.update(text.encode(encoding))
            hash_string = hash_obj.hexdigest()
            self.logger.info(f"Calculated {algorithm} hash")
            return hash_string
        
        except Exception as e:
            self.logger.error(f"Error calculating hash: {e}")
            raise
