"""
File access collector for monitoring file system operations.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set
from pathlib import Path
import hashlib

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

from .base_collector import BaseCollector


class FileAccessEventHandler(FileSystemEventHandler):
    """
    File system event handler for watchdog.
    """
    
    def __init__(self, collector):
        self.collector = collector
        self.events = []
    
    def on_modified(self, event):
        if not event.is_directory:
            self._record_event('file_modified', event.src_path)
    
    def on_created(self, event):
        if not event.is_directory:
            self._record_event('file_created', event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            self._record_event('file_deleted', event.src_path)
    
    def on_moved(self, event):
        if not event.is_directory:
            self._record_event('file_moved', event.src_path, event.dest_path)
    
    def _record_event(self, event_type: str, src_path: str, dest_path: str = None):
        """Record a file system event."""
        event_data = {
            'event_type': event_type,
            'file_path': src_path,
            'dest_path': dest_path,
            'timestamp': datetime.now().isoformat(),
            'file_size': self._get_file_size(src_path),
            'file_extension': Path(src_path).suffix.lower(),
            'risk_score': self._calculate_risk_score(src_path, event_type)
        }
        
        self.events.append(event_data)
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size safely."""
        try:
            return os.path.getsize(file_path)
        except (OSError, FileNotFoundError):
            return 0
    
    def _calculate_risk_score(self, file_path: str, event_type: str) -> float:
        """Calculate risk score for file operation."""
        risk_score = 0.1  # Base risk
        
        # High-risk file extensions
        high_risk_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.js', '.jar',
            '.msi', '.dll', '.sys', '.ps1', '.sh', '.py', '.pl'
        }
        
        # Sensitive directories
        sensitive_dirs = {
            'system32', 'windows', 'program files', 'etc', 'usr', 'var',
            'documents', 'desktop', 'downloads'
        }
        
        file_path_lower = file_path.lower()
        extension = Path(file_path).suffix.lower()
        
        # Check file extension risk
        if extension in high_risk_extensions:
            risk_score += 0.3
        
        # Check directory sensitivity
        for sensitive_dir in sensitive_dirs:
            if sensitive_dir in file_path_lower:
                risk_score += 0.2
                break
        
        # Higher risk for deletions and moves
        if event_type in ['file_deleted', 'file_moved']:
            risk_score += 0.2
        
        # Mass operations (detected by collector)
        if hasattr(self.collector, '_recent_operations'):
            recent_count = len([op for op in self.collector._recent_operations 
                              if time.time() - op < 60])  # Last minute
            if recent_count > 10:
                risk_score += 0.3
        
        return min(risk_score, 1.0)


class FileAccessCollector(BaseCollector):
    """
    Collects file access and modification events.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.monitored_directories = config.get('monitored_directories', [])
        self.observers = []
        self.event_handlers = []
        self.last_check_time = datetime.now() - timedelta(hours=1)
        self._recent_operations = []
        
        # Set default directories if none provided
        if not self.monitored_directories:
            self.monitored_directories = self._get_default_directories()
        
        self._setup_file_monitoring()
    
    def get_collector_name(self) -> str:
        return "FileAccessCollector"
    
    def _get_default_directories(self) -> List[str]:
        """Get default directories to monitor based on OS."""
        import platform
        import os
        
        directories = []
        
        if platform.system() == "Windows":
            user_profile = os.path.expanduser("~")
            directories = [
                os.path.join(user_profile, "Documents"),
                os.path.join(user_profile, "Desktop"),
                os.path.join(user_profile, "Downloads"),
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                "C:\\Windows\\System32"
            ]
        else:
            directories = [
                "/home",
                "/var/log",
                "/etc",
                "/usr/bin",
                "/opt",
                "/tmp"
            ]
        
        # Filter to existing directories
        return [d for d in directories if os.path.exists(d)]
    
    def _setup_file_monitoring(self):
        """Set up real-time file monitoring if watchdog is available."""
        if not WATCHDOG_AVAILABLE:
            self.logger.warning("Watchdog library not available. Real-time monitoring disabled.")
            return
        
        for directory in self.monitored_directories:
            if os.path.exists(directory):
                try:
                    event_handler = FileAccessEventHandler(self)
                    observer = Observer()
                    observer.schedule(event_handler, directory, recursive=True)
                    
                    self.event_handlers.append(event_handler)
                    self.observers.append(observer)
                    
                    observer.start()
                    self.logger.info(f"Started monitoring directory: {directory}")
                
                except Exception as e:
                    self.logger.error(f"Failed to monitor directory {directory}: {str(e)}")
    
    def collect_data(self) -> List[Dict[str, Any]]:
        """
        Collect file access data.
        
        Returns:
            List of file access event dictionaries
        """
        events = []
        
        # Collect events from watchdog handlers
        if WATCHDOG_AVAILABLE:
            events.extend(self._collect_watchdog_events())
        
        # Collect historical file access data
        events.extend(self._collect_historical_file_data())
        
        # Analyze for suspicious patterns
        events.extend(self._analyze_file_patterns())
        
        # Clean up old recent operations
        current_time = time.time()
        self._recent_operations = [op for op in self._recent_operations 
                                 if current_time - op < 3600]  # Keep last hour
        
        # Update last check time
        self.last_check_time = datetime.now()
        
        return events
    
    def _collect_watchdog_events(self) -> List[Dict[str, Any]]:
        """Collect events from watchdog handlers."""
        events = []
        
        for handler in self.event_handlers:
            for event_data in handler.events:
                # Add current user info
                event_data['user_id'] = os.getenv('USER', os.getenv('USERNAME', 'unknown'))
                event_data['machine_name'] = os.getenv('COMPUTERNAME', os.getenv('HOSTNAME', 'unknown'))
                
                formatted_event = self.format_event(
                    event_data, 
                    event_data['event_type'], 
                    event_data['user_id']
                )
                events.append(formatted_event)
                
                # Track recent operations
                self._recent_operations.append(time.time())
            
            # Clear collected events
            handler.events = []
        
        return events
    
    def _collect_historical_file_data(self) -> List[Dict[str, Any]]:
        """Collect historical file access information."""
        events = []
        current_user = os.getenv('USER', os.getenv('USERNAME', 'unknown'))
        machine_name = os.getenv('COMPUTERNAME', os.getenv('HOSTNAME', 'unknown'))
        
        for directory in self.monitored_directories[:3]:  # Limit to first 3 dirs for performance
            if not os.path.exists(directory):
                continue
            
            try:
                for root, dirs, files in os.walk(directory):
                    # Limit depth and number of files for performance
                    if root.count(os.sep) - directory.count(os.sep) > 2:
                        continue
                    
                    for file in files[:50]:  # Limit to first 50 files per directory
                        file_path = os.path.join(root, file)
                        
                        try:
                            stat_info = os.stat(file_path)
                            access_time = datetime.fromtimestamp(stat_info.st_atime)
                            modify_time = datetime.fromtimestamp(stat_info.st_mtime)
                            
                            # Only include recently accessed files
                            if access_time > self.last_check_time:
                                event_data = {
                                    'file_path': file_path,
                                    'access_time': access_time.isoformat(),
                                    'modify_time': modify_time.isoformat(),
                                    'file_size': stat_info.st_size,
                                    'file_extension': Path(file_path).suffix.lower(),
                                    'user_id': current_user,
                                    'machine_name': machine_name,
                                    'risk_score': self._assess_file_risk(file_path, stat_info.st_size)
                                }
                                
                                formatted_event = self.format_event(
                                    event_data, 
                                    'file_access_historical', 
                                    current_user
                                )
                                events.append(formatted_event)
                        
                        except (OSError, PermissionError):
                            continue
                    
                    # Don't recurse into too many directories
                    dirs[:] = dirs[:10]
            
            except Exception as e:
                self.logger.error(f"Error scanning directory {directory}: {str(e)}")
        
        return events
    
    def _analyze_file_patterns(self) -> List[Dict[str, Any]]:
        """Analyze file access patterns for anomalies."""
        events = []
        current_user = os.getenv('USER', os.getenv('USERNAME', 'unknown'))
        
        # Check for mass file operations
        if len(self._recent_operations) > 20:  # More than 20 operations recently
            event_data = {
                'anomaly_type': 'mass_file_operations',
                'operation_count': len(self._recent_operations),
                'time_window': '1_hour',
                'user_id': current_user,
                'machine_name': os.getenv('COMPUTERNAME', os.getenv('HOSTNAME', 'unknown')),
                'risk_score': min(0.8, len(self._recent_operations) / 50.0)
            }
            
            formatted_event = self.format_event(
                event_data, 
                'mass_file_access_anomaly', 
                current_user
            )
            events.append(formatted_event)
        
        return events
    
    def _assess_file_risk(self, file_path: str, file_size: int) -> float:
        """Assess risk level for file access."""
        risk_score = 0.1
        
        # Check file extension
        extension = Path(file_path).suffix.lower()
        high_risk_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.js', '.jar',
            '.msi', '.dll', '.sys', '.ps1', '.sh', '.py', '.pl', '.sql'
        }
        
        if extension in high_risk_extensions:
            risk_score += 0.3
        
        # Check file size (very large files might indicate data exfiltration)
        if file_size > 100 * 1024 * 1024:  # > 100MB
            risk_score += 0.2
        elif file_size > 1024 * 1024 * 1024:  # > 1GB
            risk_score += 0.4
        
        # Check file path for sensitive locations
        file_path_lower = file_path.lower()
        sensitive_keywords = [
            'password', 'secret', 'key', 'confidential', 'private',
            'admin', 'config', 'database', 'backup'
        ]
        
        for keyword in sensitive_keywords:
            if keyword in file_path_lower:
                risk_score += 0.2
                break
        
        return min(risk_score, 1.0)
    
    def stop_monitoring(self):
        """Stop file monitoring observers."""
        for observer in self.observers:
            observer.stop()
            observer.join()
        
        self.observers.clear()
        self.event_handlers.clear()
        self.logger.info("Stopped file monitoring")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self.stop_monitoring()
        except:
            pass