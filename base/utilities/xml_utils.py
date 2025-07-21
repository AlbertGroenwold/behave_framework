import logging
from typing import List
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom


class XmlUtils:
    """Utility class for working with XML data"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def read_xml_file(self, file_path: str) -> ET.Element:
        """
        Read XML data from file
        
        Args:
            file_path (str): Path to XML file
        
        Returns:
            ET.Element: Root element of XML
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            self.logger.info(f"Successfully read XML file: {file_path}")
            return root
        
        except Exception as e:
            self.logger.error(f"Error reading XML file {file_path}: {e}")
            raise
    
    def write_xml_file(self, root: ET.Element, file_path: str, pretty: bool = True) -> bool:
        """
        Write XML data to file
        
        Args:
            root (ET.Element): Root element
            file_path (str): Path to XML file
            pretty (bool): Whether to format XML prettily
        
        Returns:
            bool: True if successful
        """
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            if pretty:
                xml_str = ET.tostring(root, encoding='unicode')
                dom = minidom.parseString(xml_str)
                pretty_xml = dom.toprettyxml(indent="  ")
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(pretty_xml)
            else:
                tree = ET.ElementTree(root)
                tree.write(file_path, encoding='utf-8', xml_declaration=True)
            
            self.logger.info(f"Successfully wrote XML file: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error writing XML file {file_path}: {e}")
            return False
    
    def find_elements(self, root: ET.Element, xpath: str) -> List[ET.Element]:
        """
        Find elements using XPath
        
        Args:
            root (ET.Element): Root element
            xpath (str): XPath expression
        
        Returns:
            List[ET.Element]: List of matching elements
        """
        try:
            elements = root.findall(xpath)
            self.logger.info(f"XPath query '{xpath}' returned {len(elements)} elements")
            return elements
        
        except Exception as e:
            self.logger.error(f"Error finding elements with XPath '{xpath}': {e}")
            raise
