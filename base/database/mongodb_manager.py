import pymongo
import logging
from typing import Dict, Any, List, Optional, Union
from .base_database_manager import BaseDatabaseManager


class MongoDBManager(BaseDatabaseManager):
    """MongoDB database manager"""
    
    def __init__(self, config_path: str = None):
        super().__init__(config_path)
        self.db_type = "mongodb"
        self.client = None
        self.database = None
    
    def connect(self) -> bool:
        """Connect to MongoDB"""
        try:
            # Get connection details from config
            host = self.config.get('mongodb', 'host', fallback='localhost')
            port = self.config.get('mongodb', 'port', fallback='27017')
            database = self.config.get('mongodb', 'database', fallback='testdb')
            username = self.config.get('mongodb', 'username', fallback=None)
            password = self.config.get('mongodb', 'password', fallback=None)
            
            if username and password:
                connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}"
            else:
                connection_string = f"mongodb://{host}:{port}"
            
            self.client = pymongo.MongoClient(connection_string)
            self.database = self.client[database]
            
            # Test connection
            self.client.admin.command('ping')
            
            self.connection = self.client
            self.logger.info(f"Connected to MongoDB database: {database}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.connection = None
            self.database = None
            self.logger.info("Disconnected from MongoDB")
    
    def execute_query(self, collection_name: str, operation: str, query: Dict = None, 
                     document: Dict = None, update: Dict = None) -> Dict[str, Any]:
        """Execute MongoDB operation"""
        self.log_query(f"{operation} on {collection_name}", query or document or update)
        
        try:
            collection = self.database[collection_name]
            
            if operation == 'find':
                cursor = collection.find(query or {})
                data = list(cursor)
                return {
                    'success': True,
                    'data': data,
                    'row_count': len(data)
                }
            
            elif operation == 'insert_one':
                result = collection.insert_one(document)
                return {
                    'success': True,
                    'inserted_id': str(result.inserted_id),
                    'affected_rows': 1
                }
            
            elif operation == 'insert_many':
                result = collection.insert_many(document)
                return {
                    'success': True,
                    'inserted_ids': [str(id) for id in result.inserted_ids],
                    'affected_rows': len(result.inserted_ids)
                }
            
            elif operation == 'update_one':
                result = collection.update_one(query, update)
                return {
                    'success': True,
                    'matched_count': result.matched_count,
                    'modified_count': result.modified_count,
                    'affected_rows': result.modified_count
                }
            
            elif operation == 'update_many':
                result = collection.update_many(query, update)
                return {
                    'success': True,
                    'matched_count': result.matched_count,
                    'modified_count': result.modified_count,
                    'affected_rows': result.modified_count
                }
            
            elif operation == 'delete_one':
                result = collection.delete_one(query)
                return {
                    'success': True,
                    'deleted_count': result.deleted_count,
                    'affected_rows': result.deleted_count
                }
            
            elif operation == 'delete_many':
                result = collection.delete_many(query)
                return {
                    'success': True,
                    'deleted_count': result.deleted_count,
                    'affected_rows': result.deleted_count
                }
            
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        
        except Exception as e:
            self.logger.error(f"MongoDB operation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_row_count(self, collection_name: str) -> int:
        """Get document count for MongoDB collection"""
        try:
            collection = self.database[collection_name]
            return collection.count_documents({})
        except Exception:
            return 0
