"""
Real-time data processor that coordinates data collection and anomaly detection.
"""

import logging
import threading
import time
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from .anomaly_engine import AnomalyEngine
from data_collectors.system_events_collector import SystemEventsCollector
from data_collectors.file_access_collector import FileAccessCollector
from data_collectors.app_usage_collector import ApplicationUsageCollector


class RealTimeDataProcessor:
    """
    Coordinates real-time data collection and anomaly detection.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core components
        self.anomaly_engine = AnomalyEngine(config.get('anomaly_engine', {}))
        self.collectors = {}
        
        # Threading
        self.is_running = False
        self.collection_threads = {}
        self.scheduler_thread = None
        
        # Collection intervals (in seconds)
        self.collection_intervals = config.get('collection_intervals', {
            'system_events': 30,
            'file_access': 60,
            'app_usage': 45
        })
        
        # Performance monitoring
        self.performance_stats = {
            'total_events_collected': 0,
            'collection_errors': 0,
            'last_collection_times': {},
            'start_time': datetime.now()
        }
        
        # Initialize collectors
        self._initialize_collectors()
        
        # Setup alert handling
        self._setup_alert_handling()
    
    def _initialize_collectors(self):
        """Initialize data collectors."""
        try:
            collector_configs = self.config.get('collectors', {})
            
            # System Events Collector
            if collector_configs.get('system_events', {}).get('enabled', True):
                self.collectors['system_events'] = SystemEventsCollector(
                    collector_configs.get('system_events', {})
                )
                self.logger.info("Initialized System Events Collector")
            
            # File Access Collector
            if collector_configs.get('file_access', {}).get('enabled', True):
                self.collectors['file_access'] = FileAccessCollector(
                    collector_configs.get('file_access', {})
                )
                self.logger.info("Initialized File Access Collector")
            
            # Application Usage Collector
            if collector_configs.get('app_usage', {}).get('enabled', True):
                self.collectors['app_usage'] = ApplicationUsageCollector(
                    collector_configs.get('app_usage', {})
                )
                self.logger.info("Initialized Application Usage Collector")
        
        except Exception as e:
            self.logger.error(f"Error initializing collectors: {str(e)}")
    
    def _setup_alert_handling(self):
        """Setup alert handling callbacks."""
        try:
            # Add callback to anomaly engine for handling alerts
            self.anomaly_engine.add_alert_callback(self._handle_alert)
            
        except Exception as e:
            self.logger.error(f"Error setting up alert handling: {str(e)}")
    
    def start(self):
        """Start the real-time data processing system."""
        if self.is_running:
            self.logger.warning("Data processor is already running")
            return
        
        try:
            self.logger.info("Starting Real-Time Data Processor...")
            
            # Start anomaly detection engine
            self.anomaly_engine.start()
            
            # Start collectors in separate threads
            self._start_collectors()
            
            # Start scheduler for periodic tasks
            self._start_scheduler()
            
            self.is_running = True
            self.logger.info("Real-Time Data Processor started successfully")
        
        except Exception as e:
            self.logger.error(f"Error starting data processor: {str(e)}")
            self.stop()
    
    def stop(self):
        """Stop the real-time data processing system."""
        if not self.is_running:
            return
        
        try:
            self.logger.info("Stopping Real-Time Data Processor...")
            
            self.is_running = False
            
            # Stop collectors
            self._stop_collectors()
            
            # Stop scheduler
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            # Stop anomaly engine
            self.anomaly_engine.stop()
            
            self.logger.info("Real-Time Data Processor stopped")
        
        except Exception as e:
            self.logger.error(f"Error stopping data processor: {str(e)}")
    
    def _start_collectors(self):
        """Start all data collectors in separate threads."""
        for name, collector in self.collectors.items():
            try:
                interval = self.collection_intervals.get(name, 60)
                
                def collection_worker(collector_name, collector_instance, collection_interval):
                    """Worker function for continuous data collection."""
                    while self.is_running:
                        try:
                            start_time = time.time()
                            
                            # Collect data
                            events = collector_instance.collect_data()
                            
                            # Process events through anomaly engine
                            for event in events:
                                success = self.anomaly_engine.add_event(event)
                                if success:
                                    self.performance_stats['total_events_collected'] += 1
                            
                            # Update performance stats
                            self.performance_stats['last_collection_times'][collector_name] = datetime.now()
                            
                            # Calculate processing time and sleep
                            processing_time = time.time() - start_time
                            sleep_time = max(0, collection_interval - processing_time)
                            
                            if sleep_time > 0:
                                time.sleep(sleep_time)
                        
                        except Exception as e:
                            self.logger.error(f"Error in {collector_name} collection: {str(e)}")
                            self.performance_stats['collection_errors'] += 1
                            time.sleep(5)  # Wait before retrying
                
                thread = threading.Thread(
                    target=collection_worker,
                    args=(name, collector, interval),
                    daemon=True,
                    name=f"collector_{name}"
                )
                
                thread.start()
                self.collection_threads[name] = thread
                
                self.logger.info(f"Started {name} collector with {interval}s interval")
            
            except Exception as e:
                self.logger.error(f"Error starting {name} collector: {str(e)}")
    
    def _stop_collectors(self):
        """Stop all data collectors."""
        for name, thread in self.collection_threads.items():
            try:
                if thread.is_alive():
                    thread.join(timeout=5)
                    if thread.is_alive():
                        self.logger.warning(f"Collector thread {name} did not stop gracefully")
            except Exception as e:
                self.logger.error(f"Error stopping {name} collector: {str(e)}")
        
        # Stop file monitoring if active
        for name, collector in self.collectors.items():
            try:
                if hasattr(collector, 'stop_monitoring'):
                    collector.stop_monitoring()
            except Exception as e:
                self.logger.error(f"Error stopping monitoring for {name}: {str(e)}")
        
        self.collection_threads.clear()
    
    def _start_scheduler(self):
        """Start scheduler for periodic maintenance tasks."""
        def scheduler_worker():
            """Scheduler worker that runs periodic tasks."""
            # Schedule periodic tasks
            schedule.every(5).minutes.do(self._cleanup_old_sessions)
            schedule.every(15).minutes.do(self._update_user_baselines)
            schedule.every(1).hours.do(self._log_performance_stats)
            schedule.every(24).hours.do(self._cleanup_old_data)
            
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    self.logger.error(f"Error in scheduler: {str(e)}")
                    time.sleep(60)
        
        self.scheduler_thread = threading.Thread(
            target=scheduler_worker,
            daemon=True,
            name="scheduler"
        )
        self.scheduler_thread.start()
        
        self.logger.info("Started scheduler thread")
    
    def _handle_alert(self, alert: Dict[str, Any]):
        """
        Handle alerts generated by the anomaly engine.
        
        Args:
            alert: Alert dictionary
        """
        try:
            self.logger.warning(f"Processing alert: {alert['id']} - {alert['severity']}")
            
            # Here you could add additional alert handling logic:
            # - Send notifications
            # - Update database
            # - Trigger automated responses
            # - Log to SIEM systems
            
            # For now, just log the alert details
            self.logger.info(f"Alert Details: User={alert['user_context']['user_id']}, "
                            f"Score={alert['anomaly_score']:.3f}, "
                            f"Event={alert['event'].get('event_type', 'unknown')}")
        
        except Exception as e:
            self.logger.error(f"Error handling alert: {str(e)}")
    
    def _cleanup_old_sessions(self):
        """Clean up old user sessions."""
        try:
            current_time = time.time()
            session_timeout = self.config.get('session_timeout', 3600)  # 1 hour
            
            # This would be implemented in the anomaly engine
            # For now, just log that cleanup is happening
            self.logger.debug("Cleaning up old user sessions")
        
        except Exception as e:
            self.logger.error(f"Error cleaning up sessions: {str(e)}")
    
    def _update_user_baselines(self):
        """Update user behavior baselines."""
        try:
            self.logger.debug("Updating user behavior baselines")
            
            # This would involve:
            # 1. Analyzing recent user behavior
            # 2. Updating baseline models
            # 3. Adjusting detection thresholds
            
            # For now, just log that update is happening
            pass
        
        except Exception as e:
            self.logger.error(f"Error updating user baselines: {str(e)}")
    
    def _log_performance_stats(self):
        """Log performance statistics."""
        try:
            stats = self.get_performance_stats()
            self.logger.info(f"Performance Stats: {stats}")
        
        except Exception as e:
            self.logger.error(f"Error logging performance stats: {str(e)}")
    
    def _cleanup_old_data(self):
        """Clean up old data from database."""
        try:
            self.logger.info("Cleaning up old data (placeholder)")
            
            # This would involve:
            # 1. Removing old events from database
            # 2. Archiving important data
            # 3. Optimizing database performance
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {str(e)}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Returns:
            Dictionary containing performance metrics
        """
        try:
            current_time = datetime.now()
            uptime = current_time - self.performance_stats['start_time']
            
            stats = self.performance_stats.copy()
            stats.update({
                'uptime_seconds': uptime.total_seconds(),
                'events_per_second': self.performance_stats['total_events_collected'] / max(uptime.total_seconds(), 1),
                'active_collectors': len([t for t in self.collection_threads.values() if t.is_alive()]),
                'anomaly_engine_stats': self.anomaly_engine.get_statistics()
            })
            
            return stats
        
        except Exception as e:
            self.logger.error(f"Error getting performance stats: {str(e)}")
            return {}
    
    def get_collector_status(self) -> Dict[str, Any]:
        """
        Get status of all collectors.
        
        Returns:
            Dictionary containing collector status information
        """
        status = {}
        
        for name, collector in self.collectors.items():
            try:
                thread = self.collection_threads.get(name)
                status[name] = {
                    'enabled': True,
                    'running': thread.is_alive() if thread else False,
                    'last_collection': self.performance_stats['last_collection_times'].get(name),
                    'collector_type': collector.__class__.__name__
                }
            except Exception as e:
                status[name] = {
                    'enabled': False,
                    'running': False,
                    'error': str(e)
                }
        
        return status
    
    def force_collection(self, collector_name: Optional[str] = None):
        """
        Force immediate data collection.
        
        Args:
            collector_name: Name of specific collector to run, or None for all
        """
        try:
            if collector_name and collector_name in self.collectors:
                collectors_to_run = {collector_name: self.collectors[collector_name]}
            else:
                collectors_to_run = self.collectors
            
            def run_collection(name, collector):
                try:
                    events = collector.collect_data()
                    for event in events:
                        self.anomaly_engine.add_event(event)
                    self.logger.info(f"Forced collection for {name}: {len(events)} events")
                except Exception as e:
                    self.logger.error(f"Error in forced collection for {name}: {str(e)}")
            
            # Run collections in parallel
            with ThreadPoolExecutor(max_workers=len(collectors_to_run)) as executor:
                futures = []
                for name, collector in collectors_to_run.items():
                    future = executor.submit(run_collection, name, collector)
                    futures.append(future)
                
                # Wait for all collections to complete
                for future in futures:
                    future.result()
        
        except Exception as e:
            self.logger.error(f"Error in forced collection: {str(e)}")
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent alerts (placeholder - would need alert storage).
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        # This would be implemented with proper alert storage
        # For now, return empty list
        return []