#!/usr/bin/env python3
"""
System Logger - Comprehensive logging to Supabase database
Logs all key system events, user actions, and errors to system_logs table
"""

import os
import time
import json
import traceback
from typing import Optional, Dict, Any
from datetime import datetime

class SystemLogger:
    """Centralized system logger that saves to Supabase database"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.is_postgresql = self.database_url and "postgresql" in self.database_url
        
    def log(self, level: str, message: str, module: str = None, user_id: str = None, 
            extra_data: Dict[str, Any] = None, error: Exception = None):
        """
        Log system event to Supabase database
        
        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
            module: Module/component name
            user_id: User ID if applicable
            extra_data: Additional data to log
            error: Exception object if logging an error
        """
        try:
            # Prepare log entry
            log_entry = {
                'level': level.upper(),
                'message': message,
                'module': module or 'system',
                'timestamp': time.time(),
                'user_id': user_id,
                'extra_data': json.dumps(extra_data) if extra_data else None,
                'error_details': str(error) if error else None,
                'traceback': traceback.format_exc() if error else None
            }
            
            # Save to Supabase if available
            if self.is_postgresql:
                self._save_to_supabase(log_entry)
            
            # Always save to local backup
            self._save_to_local(log_entry)
            
            # Print to console for immediate visibility
            timestamp_str = datetime.fromtimestamp(log_entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            console_msg = f"[{timestamp_str}] {level.upper()}: {message}"
            if module:
                console_msg += f" (module: {module})"
            if user_id:
                console_msg += f" (user: {user_id})"
            print(console_msg)
            
        except Exception as log_error:
            # Fallback logging to prevent infinite loops
            print(f"LOGGING ERROR: Failed to log message '{message}': {log_error}")
    
    def _save_to_supabase(self, log_entry: Dict[str, Any]):
        """Save log entry to Supabase database"""
        try:
            import psycopg2
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO system_logs (level, message, module, timestamp, user_id, extra_data, error_details, traceback)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                log_entry['level'],
                log_entry['message'],
                log_entry['module'],
                log_entry['timestamp'],
                log_entry['user_id'],
                log_entry['extra_data'],
                log_entry['error_details'],
                log_entry['traceback']
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"Failed to save log to Supabase: {e}")
    
    def _save_to_local(self, log_entry: Dict[str, Any]):
        """Save log entry to local SQLite backup"""
        try:
            import sqlite3
            conn = sqlite3.connect('data.db')
            
            # Create table if not exists
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    module TEXT,
                    timestamp REAL NOT NULL,
                    user_id TEXT,
                    extra_data TEXT,
                    error_details TEXT,
                    traceback TEXT
                )
            """)
            
            cur.execute("""
                INSERT INTO system_logs (level, message, module, timestamp, user_id, extra_data, error_details, traceback)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_entry['level'],
                log_entry['message'],
                log_entry['module'],
                log_entry['timestamp'],
                log_entry['user_id'],
                log_entry['extra_data'],
                log_entry['error_details'],
                log_entry['traceback']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Failed to save log to local database: {e}")
    
    # Convenience methods for different log levels
    def info(self, message: str, module: str = None, user_id: str = None, extra_data: Dict[str, Any] = None):
        """Log INFO level message"""
        self.log('INFO', message, module, user_id, extra_data)
    
    def warning(self, message: str, module: str = None, user_id: str = None, extra_data: Dict[str, Any] = None):
        """Log WARNING level message"""
        self.log('WARNING', message, module, user_id, extra_data)
    
    def error(self, message: str, module: str = None, user_id: str = None, 
              extra_data: Dict[str, Any] = None, error: Exception = None):
        """Log ERROR level message"""
        self.log('ERROR', message, module, user_id, extra_data, error)
    
    def debug(self, message: str, module: str = None, user_id: str = None, extra_data: Dict[str, Any] = None):
        """Log DEBUG level message"""
        self.log('DEBUG', message, module, user_id, extra_data)
    
    def user_action(self, action: str, user_id: str, details: Dict[str, Any] = None):
        """Log user action"""
        self.info(f"User action: {action}", module="user_actions", user_id=user_id, extra_data=details)
    
    def system_event(self, event: str, details: Dict[str, Any] = None):
        """Log system event"""
        self.info(f"System event: {event}", module="system_events", extra_data=details)
    
    def database_operation(self, operation: str, table: str, user_id: str = None, details: Dict[str, Any] = None):
        """Log database operation"""
        self.info(f"Database {operation} on {table}", module="database", user_id=user_id, extra_data=details)
    
    def api_request(self, endpoint: str, method: str, user_id: str = None, details: Dict[str, Any] = None):
        """Log API request"""
        self.info(f"{method} {endpoint}", module="api", user_id=user_id, extra_data=details)
    
    def get_recent_logs(self, limit: int = 50, level: str = None) -> list:
        """Get recent logs from database"""
        try:
            if self.is_postgresql:
                return self._get_logs_from_supabase(limit, level)
            else:
                return self._get_logs_from_local(limit, level)
        except Exception as e:
            print(f"Failed to retrieve logs: {e}")
            return []
    
    def _get_logs_from_supabase(self, limit: int, level: str = None) -> list:
        """Get logs from Supabase"""
        try:
            import psycopg2
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            if level:
                cur.execute("""
                    SELECT level, message, module, timestamp, user_id, extra_data
                    FROM system_logs 
                    WHERE level = %s
                    ORDER BY timestamp DESC 
                    LIMIT %s
                """, (level.upper(), limit))
            else:
                cur.execute("""
                    SELECT level, message, module, timestamp, user_id, extra_data
                    FROM system_logs 
                    ORDER BY timestamp DESC 
                    LIMIT %s
                """, (limit,))
            
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            logs = []
            for row in rows:
                logs.append({
                    'level': row[0],
                    'message': row[1],
                    'module': row[2],
                    'timestamp': row[3],
                    'user_id': row[4],
                    'extra_data': json.loads(row[5]) if row[5] else None,
                    'formatted_time': datetime.fromtimestamp(row[3]).strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return logs
            
        except Exception as e:
            print(f"Failed to get logs from Supabase: {e}")
            return []
    
    def _get_logs_from_local(self, limit: int, level: str = None) -> list:
        """Get logs from local SQLite"""
        try:
            import sqlite3
            conn = sqlite3.connect('data.db')
            cur = conn.cursor()
            
            if level:
                cur.execute("""
                    SELECT level, message, module, timestamp, user_id, extra_data
                    FROM system_logs 
                    WHERE level = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (level.upper(), limit))
            else:
                cur.execute("""
                    SELECT level, message, module, timestamp, user_id, extra_data
                    FROM system_logs 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
            
            rows = cur.fetchall()
            conn.close()
            
            logs = []
            for row in rows:
                logs.append({
                    'level': row[0],
                    'message': row[1],
                    'module': row[2],
                    'timestamp': row[3],
                    'user_id': row[4],
                    'extra_data': json.loads(row[5]) if row[5] else None,
                    'formatted_time': datetime.fromtimestamp(row[3]).strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return logs
            
        except Exception as e:
            print(f"Failed to get logs from local database: {e}")
            return []

# Global logger instance
system_logger = SystemLogger()

# Convenience functions for easy import
def log_info(message: str, module: str = None, user_id: str = None, extra_data: Dict[str, Any] = None):
    system_logger.info(message, module, user_id, extra_data)

def log_warning(message: str, module: str = None, user_id: str = None, extra_data: Dict[str, Any] = None):
    system_logger.warning(message, module, user_id, extra_data)

def log_error(message: str, module: str = None, user_id: str = None, extra_data: Dict[str, Any] = None, error: Exception = None):
    system_logger.error(message, module, user_id, extra_data, error)

def log_user_action(action: str, user_id: str, details: Dict[str, Any] = None):
    system_logger.user_action(action, user_id, details)

def log_system_event(event: str, details: Dict[str, Any] = None):
    system_logger.system_event(event, details)

def log_database_operation(operation: str, table: str, user_id: str = None, details: Dict[str, Any] = None):
    system_logger.database_operation(operation, table, user_id, details)

def log_api_request(endpoint: str, method: str, user_id: str = None, details: Dict[str, Any] = None):
    system_logger.api_request(endpoint, method, user_id, details)