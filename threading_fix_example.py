#!/usr/bin/env python3
"""
SQLite Threading Fix - Example Implementation
Shows how to fix the threading issue in the enhanced logic engine
"""

import sqlite3
import threading
from typing import Dict, Any, List

class ThreadSafeEnhancedBuildingCodeEngine:
    """
    Fixed version of EnhancedBuildingCodeEngine with proper thread safety
    """
    
    def __init__(self, db_path: str = "database/building_codes.db"):
        self.db_path = db_path
        self.validation_log = []
        # Remove self.connection - create per request instead
        
    def get_connection(self):
        """
        Create a new connection for each request/thread
        This ensures thread safety
        """
        try:
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row
            return connection
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return None
    
    def match_context_logic_rules(self, normalized_inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        FIXED: Create connection per request instead of using shared connection
        """
        applicable_rules = []
        
        # Create connection for this request/thread
        connection = self.get_connection()
        if not connection:
            return applicable_rules
            
        try:
            cursor = connection.cursor()
            
            # Query all rules for the jurisdiction
            cursor.execute("""
                SELECT * FROM context_logic_rule 
                WHERE jurisdiction = ? OR jurisdiction = 'ALL'
                ORDER BY priority DESC
            """, (normalized_inputs["jurisdiction"],))
            
            all_rules = cursor.fetchall()
            
            # Process rules...
            for rule in all_rules:
                # Your existing logic here
                pass
                
        except Exception as e:
            print(f"Error in match_context_logic_rules: {e}")
        finally:
            # Always close the connection
            connection.close()
        
        return applicable_rules

# Alternative Solution: Connection Pool
import threading
from queue import Queue

class ConnectionPoolEngine:
    """
    Alternative solution using connection pooling
    """
    
    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self.connection_pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        
        # Pre-create connections
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.connection_pool.put(conn)
    
    def get_connection(self):
        """Get connection from pool"""
        return self.connection_pool.get()
    
    def return_connection(self, connection):
        """Return connection to pool"""
        self.connection_pool.put(connection)
    
    def match_context_logic_rules(self, normalized_inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Using connection pool approach
        """
        applicable_rules = []
        
        # Get connection from pool
        connection = self.get_connection()
        
        try:
            cursor = connection.cursor()
            
            # Your database operations here
            cursor.execute("""
                SELECT * FROM context_logic_rule 
                WHERE jurisdiction = ? OR jurisdiction = 'ALL'
                ORDER BY priority DESC
            """, (normalized_inputs["jurisdiction"],))
            
            all_rules = cursor.fetchall()
            
            # Process rules...
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Return connection to pool
            self.return_connection(connection)
        
        return applicable_rules

# Solution 3: Context Manager Approach
from contextlib import contextmanager

class ContextManagerEngine:
    """
    Using context manager for automatic connection handling
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if connection:
                connection.close()
    
    def match_context_logic_rules(self, normalized_inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Using context manager approach
        """
        applicable_rules = []
        
        with self.get_db_connection() as connection:
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT * FROM context_logic_rule 
                WHERE jurisdiction = ? OR jurisdiction = 'ALL'
                ORDER BY priority DESC
            """, (normalized_inputs["jurisdiction"],))
            
            all_rules = cursor.fetchall()
            
            # Process rules...
        
        return applicable_rules

# Example of how to fix your current code:
"""
BEFORE (Problematic):
class EnhancedBuildingCodeEngine:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)  # ← Created in main thread
    
    def match_context_logic_rules(self, inputs):
        cursor = self.connection.cursor()  # ← Used in request thread - FAILS!

AFTER (Fixed):
class EnhancedBuildingCodeEngine:
    def __init__(self, db_path):
        self.db_path = db_path  # ← Store path, not connection
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)  # ← Create per request
    
    def match_context_logic_rules(self, inputs):
        with self.get_connection() as connection:  # ← Thread-safe
            cursor = connection.cursor()
""" 