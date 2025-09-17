"""
Base collector class for all data collection modules.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any
import sqlite3
import os

class BaseCollector(ABC):
    """
    Abstract base class for all data collectors.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_path = config.get('database_path', 'data/threat_detection.db')
        self._init_database()
    
    def _init_database(self):
        """Initialize the database and create tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create main events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    source_ip TEXT,
                    machine_name TEXT,
                    event_data TEXT,
                    risk_score REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create anomalies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER,
                    anomaly_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    description TEXT,
                    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES user_events (id)
                )
            ''')
            
            # Create user profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    normal_login_hours TEXT,
                    common_applications TEXT,
                    typical_file_access_patterns TEXT,
                    baseline_activity_level REAL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    @abstractmethod
    def collect_data(self) -> List[Dict[str, Any]]:
        """
        Collect data from the specific source.
        
        Returns:
            List of event dictionaries
        """
        pass
    
    @abstractmethod
    def get_collector_name(self) -> str:
        """
        Get the name of this collector.
        
        Returns:
            Collector name as string
        """
        pass
    
    def save_event(self, event_data: Dict[str, Any]) -> int:
        """
        Save an event to the database.
        
        Args:
            event_data: Dictionary containing event information
            
        Returns:
            The ID of the saved event
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_events 
                (user_id, event_type, timestamp, source_ip, machine_name, event_data, risk_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_data.get('user_id', ''),
                event_data.get('event_type', ''),
                event_data.get('timestamp', datetime.now().isoformat()),
                event_data.get('source_ip', ''),
                event_data.get('machine_name', ''),
                json.dumps(event_data),
                event_data.get('risk_score', 0.0)
            ))
            
            event_id = cursor.lastrowid
            conn.commit()
            return event_id
    
    def save_events(self, events: List[Dict[str, Any]]) -> List[int]:
        """
        Save multiple events to the database.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of event IDs
        """
        event_ids = []
        for event in events:
            event_id = self.save_event(event)
            event_ids.append(event_id)
        
        return event_ids
    
    def get_user_baseline(self, user_id: str) -> Dict[str, Any]:
        """
        Get baseline behavior for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary containing baseline behavior data
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM user_profiles WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            
            return {}
    
    def update_user_baseline(self, user_id: str, baseline_data: Dict[str, Any]):
        """
        Update user baseline behavior.
        
        Args:
            user_id: User identifier
            baseline_data: Dictionary containing baseline data
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_profiles 
                (user_id, normal_login_hours, common_applications, 
                 typical_file_access_patterns, baseline_activity_level, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                json.dumps(baseline_data.get('normal_login_hours', [])),
                json.dumps(baseline_data.get('common_applications', [])),
                json.dumps(baseline_data.get('typical_file_access_patterns', [])),
                baseline_data.get('baseline_activity_level', 0.0),
                datetime.now().isoformat()
            ))
            
            conn.commit()
    
    def start_collection(self):
        """
        Start the data collection process.
        """
        self.logger.info(f"Starting {self.get_collector_name()} collector")
        try:
            events = self.collect_data()
            if events:
                event_ids = self.save_events(events)
                self.logger.info(f"Collected and saved {len(event_ids)} events")
            else:
                self.logger.debug("No new events collected")
        except Exception as e:
            self.logger.error(f"Error in data collection: {str(e)}")
    
    def format_event(self, raw_data: Dict[str, Any], event_type: str, user_id: str) -> Dict[str, Any]:
        """
        Format raw data into a standardized event format.
        
        Args:
            raw_data: Raw event data
            event_type: Type of event
            user_id: User identifier
            
        Returns:
            Formatted event dictionary
        """
        return {
            'user_id': user_id,
            'event_type': event_type,
            'timestamp': raw_data.get('timestamp', datetime.now().isoformat()),
            'source_ip': raw_data.get('source_ip', ''),
            'machine_name': raw_data.get('machine_name', ''),
            'collector': self.get_collector_name(),
            'raw_data': raw_data
        }