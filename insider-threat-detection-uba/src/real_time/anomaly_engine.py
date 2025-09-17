"""
Real-time anomaly detection engine that processes events and detects threats.
"""

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from queue import Queue, Empty
import numpy as np
import pandas as pd

from ml_models.isolation_forest_model import IsolationForestModel
from ml_models.autoencoder_model import AutoencoderModel
from data_collectors.base_collector import BaseCollector


class AnomalyEngine:
    """
    Real-time anomaly detection engine that processes incoming events
    and identifies potential insider threats.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Event processing
        self.event_queue = Queue(maxsize=config.get('queue_max_size', 1000))
        self.processing_thread = None
        self.is_running = False
        
        # Models
        self.models = {}
        self.model_weights = config.get('model_weights', {
            'isolation_forest': 0.6,
            'autoencoder': 0.4
        })
        
        # Alert thresholds
        self.alert_threshold = config.get('alert_threshold', 0.7)
        self.high_alert_threshold = config.get('high_alert_threshold', 0.9)
        
        # Event batching
        self.batch_size = config.get('batch_size', 10)
        self.batch_timeout = config.get('batch_timeout', 30)  # seconds
        self.event_batch = []
        self.last_batch_time = time.time()
        
        # User behavior tracking
        self.user_sessions = {}
        self.user_baselines = {}
        
        # Alert callbacks
        self.alert_callbacks = []
        
        # Statistics
        self.stats = {
            'events_processed': 0,
            'anomalies_detected': 0,
            'alerts_generated': 0,
            'start_time': datetime.now()
        }
        
        # Load models
        self._load_models()
    
    def _load_models(self):
        """Load ML models for anomaly detection."""
        try:
            # Initialize Isolation Forest
            if_config = self.config.get('isolation_forest', {})
            self.models['isolation_forest'] = IsolationForestModel(if_config)
            
            # Initialize Autoencoder
            ae_config = self.config.get('autoencoder', {})
            self.models['autoencoder'] = AutoencoderModel(ae_config)
            
            # Load pre-trained models if available
            for model_name, model in self.models.items():
                model_path = self.config.get(f'{model_name}_model_path')
                if model_path:
                    try:
                        success = model.load_model(model_path)
                        if success:
                            self.logger.info(f"Loaded pre-trained {model_name} model")
                        else:
                            self.logger.warning(f"Failed to load {model_name} model from {model_path}")
                    except Exception as e:
                        self.logger.error(f"Error loading {model_name} model: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Error initializing models: {str(e)}")
    
    def start(self):
        """Start the real-time anomaly detection engine."""
        if self.is_running:
            self.logger.warning("Engine is already running")
            return
        
        self.is_running = True
        self.processing_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processing_thread.start()
        
        self.logger.info("Anomaly detection engine started")
    
    def stop(self):
        """Stop the anomaly detection engine."""
        self.is_running = False
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5)
        
        # Process remaining events in batch
        if self.event_batch:
            self._process_batch()
        
        self.logger.info("Anomaly detection engine stopped")
    
    def add_event(self, event: Dict[str, Any]) -> bool:
        """
        Add an event to the processing queue.
        
        Args:
            event: Event data dictionary
            
        Returns:
            True if event was queued successfully, False otherwise
        """
        try:
            if not self.is_running:
                self.logger.warning("Engine is not running")
                return False
            
            # Add timestamp if not present
            if 'timestamp' not in event:
                event['timestamp'] = datetime.now().isoformat()
            
            # Try to add to queue (non-blocking)
            try:
                self.event_queue.put(event, block=False)
                return True
            except:
                self.logger.warning("Event queue is full, dropping event")
                return False
        
        except Exception as e:
            self.logger.error(f"Error adding event to queue: {str(e)}")
            return False
    
    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Add a callback function that will be called when an alert is generated.
        
        Args:
            callback: Function that takes an alert dictionary as parameter
        """
        self.alert_callbacks.append(callback)
    
    def _process_events(self):
        """Main event processing loop (runs in separate thread)."""
        while self.is_running:
            try:
                # Get events from queue
                try:
                    event = self.event_queue.get(timeout=1.0)
                    self.event_batch.append(event)
                    self.event_queue.task_done()
                except Empty:
                    # No new events, check if we should process current batch
                    pass
                
                # Check if we should process the current batch
                current_time = time.time()
                should_process_batch = (
                    len(self.event_batch) >= self.batch_size or
                    (self.event_batch and current_time - self.last_batch_time >= self.batch_timeout)
                )
                
                if should_process_batch:
                    self._process_batch()
                    self.last_batch_time = current_time
            
            except Exception as e:
                self.logger.error(f"Error in event processing loop: {str(e)}")
                time.sleep(1)
    
    def _process_batch(self):
        """Process a batch of events for anomaly detection."""
        if not self.event_batch:
            return
        
        try:
            self.logger.debug(f"Processing batch of {len(self.event_batch)} events")
            
            # Convert events to DataFrame for processing
            df = pd.DataFrame(self.event_batch)
            
            # Update user sessions
            self._update_user_sessions(df)
            
            # Preprocess events for ML models
            processed_events = self._preprocess_events(df)
            
            if processed_events.empty:
                self.event_batch = []
                return
            
            # Run anomaly detection
            anomaly_results = self._detect_anomalies(processed_events)
            
            # Process results and generate alerts
            self._process_anomaly_results(anomaly_results, self.event_batch)
            
            # Update statistics
            self.stats['events_processed'] += len(self.event_batch)
            
            # Clear processed batch
            self.event_batch = []
        
        except Exception as e:
            self.logger.error(f"Error processing event batch: {str(e)}")
            # Clear batch to prevent repeated errors
            self.event_batch = []
    
    def _preprocess_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess events for anomaly detection.
        
        Args:
            df: DataFrame containing events
            
        Returns:
            Preprocessed DataFrame
        """
        try:
            # Basic preprocessing similar to base model
            processed_df = df.copy()
            
            # Add derived features
            if 'timestamp' in processed_df.columns:
                processed_df['timestamp'] = pd.to_datetime(processed_df['timestamp'])
                processed_df['hour'] = processed_df['timestamp'].dt.hour
                processed_df['day_of_week'] = processed_df['timestamp'].dt.dayofweek
                processed_df['is_weekend'] = (processed_df['timestamp'].dt.dayofweek >= 5).astype(int)
                processed_df['is_off_hours'] = ((processed_df['timestamp'].dt.hour < 7) | 
                                              (processed_df['timestamp'].dt.hour > 19)).astype(int)
            
            # Add user behavior features
            if 'user_id' in processed_df.columns:
                for idx, row in processed_df.iterrows():
                    user_id = row['user_id']
                    if user_id in self.user_sessions:
                        session = self.user_sessions[user_id]
                        processed_df.loc[idx, 'session_event_count'] = session.get('event_count', 0)
                        processed_df.loc[idx, 'session_duration'] = session.get('duration', 0)
                        processed_df.loc[idx, 'user_risk_score'] = session.get('risk_score', 0.0)
            
            return processed_df
        
        except Exception as e:
            self.logger.error(f"Error preprocessing events: {str(e)}")
            return pd.DataFrame()
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Run anomaly detection on preprocessed events.
        
        Args:
            df: Preprocessed events DataFrame
            
        Returns:
            List of anomaly detection results
        """
        results = []
        
        try:
            for model_name, model in self.models.items():
                if not model.is_trained:
                    # Skip untrained models
                    continue
                
                try:
                    # Preprocess data for this model
                    X, _ = model.preprocess_data(df)
                    
                    if X.size == 0:
                        continue
                    
                    # Get predictions
                    if hasattr(model, 'detect_anomalies'):
                        model_results = model.detect_anomalies(X, return_scores=True)
                    else:
                        predictions = model.predict(X)
                        model_results = {
                            'predictions': predictions,
                            'anomaly_indices': np.where(predictions == -1)[0].tolist()
                        }
                    
                    # Add model info to results
                    model_results['model_name'] = model_name
                    model_results['model_weight'] = self.model_weights.get(model_name, 1.0)
                    
                    results.append(model_results)
                
                except Exception as e:
                    self.logger.error(f"Error running {model_name} model: {str(e)}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error in anomaly detection: {str(e)}")
        
        return results
    
    def _process_anomaly_results(self, results: List[Dict[str, Any]], original_events: List[Dict[str, Any]]):
        """
        Process anomaly detection results and generate alerts.
        
        Args:
            results: List of model results
            original_events: Original event data
        """
        try:
            if not results:
                return
            
            # Combine results from multiple models
            combined_scores = self._combine_model_results(results, len(original_events))
            
            # Generate alerts for high-scoring events
            for i, (event, score) in enumerate(zip(original_events, combined_scores)):
                if score >= self.alert_threshold:
                    alert = self._create_alert(event, score, i, results)
                    self._trigger_alert(alert)
                    
                    self.stats['anomalies_detected'] += 1
                    if score >= self.high_alert_threshold:
                        self.stats['alerts_generated'] += 1
        
        except Exception as e:
            self.logger.error(f"Error processing anomaly results: {str(e)}")
    
    def _combine_model_results(self, results: List[Dict[str, Any]], num_events: int) -> List[float]:
        """
        Combine results from multiple models using weighted voting.
        
        Args:
            results: List of model results
            num_events: Number of events in the batch
            
        Returns:
            List of combined anomaly scores
        """
        combined_scores = np.zeros(num_events)
        total_weight = 0.0
        
        for result in results:
            model_name = result.get('model_name', 'unknown')
            weight = result.get('model_weight', 1.0)
            
            # Get anomaly scores or convert predictions to scores
            if 'anomaly_scores' in result:
                scores = np.array(result['anomaly_scores'])
                # Normalize scores to 0-1 range
                if len(scores) > 0:
                    scores = (scores - np.min(scores)) / (np.max(scores) - np.min(scores) + 1e-8)
            elif 'predictions' in result:
                # Convert predictions (-1/1) to scores (0-1)
                predictions = np.array(result['predictions'])
                scores = (predictions == -1).astype(float)
            else:
                continue
            
            # Add weighted scores
            if len(scores) == num_events:
                combined_scores += weight * scores
                total_weight += weight
        
        # Normalize by total weight
        if total_weight > 0:
            combined_scores /= total_weight
        
        return combined_scores.tolist()
    
    def _create_alert(self, event: Dict[str, Any], score: float, event_index: int, 
                     model_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create an alert dictionary from an anomalous event.
        
        Args:
            event: Original event data
            score: Anomaly score
            event_index: Index of the event in the batch
            model_results: Results from all models
            
        Returns:
            Alert dictionary
        """
        alert = {
            'id': f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{event_index}",
            'timestamp': datetime.now().isoformat(),
            'severity': self._get_severity_level(score),
            'anomaly_score': float(score),
            'event': event.copy(),
            'detection_details': {
                'models_used': [r.get('model_name') for r in model_results],
                'combined_score': float(score),
                'threshold': self.alert_threshold
            },
            'user_context': self._get_user_context(event.get('user_id')),
            'recommended_actions': self._get_recommended_actions(event, score)
        }
        
        return alert
    
    def _get_severity_level(self, score: float) -> str:
        """
        Determine severity level based on anomaly score.
        
        Args:
            score: Anomaly score (0-1)
            
        Returns:
            Severity level string
        """
        if score >= self.high_alert_threshold:
            return "HIGH"
        elif score >= self.alert_threshold:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get user context information for the alert.
        
        Args:
            user_id: User identifier
            
        Returns:
            User context dictionary
        """
        context = {
            'user_id': user_id,
            'session_info': self.user_sessions.get(user_id, {}),
            'baseline_info': self.user_baselines.get(user_id, {})
        }
        
        return context
    
    def _get_recommended_actions(self, event: Dict[str, Any], score: float) -> List[str]:
        """
        Generate recommended actions based on the event and anomaly score.
        
        Args:
            event: Event data
            score: Anomaly score
            
        Returns:
            List of recommended action strings
        """
        actions = []
        
        if score >= self.high_alert_threshold:
            actions.append("Immediately investigate user activity")
            actions.append("Consider temporarily suspending user access")
            actions.append("Notify security team and management")
        elif score >= self.alert_threshold:
            actions.append("Review user's recent activity")
            actions.append("Monitor user closely for additional anomalies")
            actions.append("Notify security analyst for review")
        
        # Event-specific recommendations
        event_type = event.get('event_type', '')
        
        if 'login' in event_type.lower():
            actions.append("Verify login location and device")
            actions.append("Check for concurrent sessions")
        elif 'file' in event_type.lower():
            actions.append("Review file access patterns")
            actions.append("Check if files contain sensitive data")
        elif 'command' in event_type.lower():
            actions.append("Analyze command for malicious intent")
            actions.append("Check command execution context")
        
        return actions
    
    def _trigger_alert(self, alert: Dict[str, Any]):
        """
        Trigger an alert by calling all registered callbacks.
        
        Args:
            alert: Alert dictionary
        """
        try:
            self.logger.warning(f"ANOMALY DETECTED: {alert['severity']} severity, "
                               f"score: {alert['anomaly_score']:.3f}, "
                               f"user: {alert['event'].get('user_id', 'unknown')}")
            
            # Call all registered callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"Error in alert callback: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Error triggering alert: {str(e)}")
    
    def _update_user_sessions(self, df: pd.DataFrame):
        """
        Update user session information.
        
        Args:
            df: DataFrame containing events
        """
        try:
            for _, event in df.iterrows():
                user_id = event.get('user_id')
                if not user_id:
                    continue
                
                current_time = time.time()
                
                if user_id not in self.user_sessions:
                    self.user_sessions[user_id] = {
                        'start_time': current_time,
                        'last_activity': current_time,
                        'event_count': 0,
                        'risk_score': 0.0,
                        'event_types': set()
                    }
                
                session = self.user_sessions[user_id]
                session['last_activity'] = current_time
                session['event_count'] += 1
                session['duration'] = current_time - session['start_time']
                
                # Update risk score based on event
                event_risk = event.get('risk_score', 0.0)
                if isinstance(event_risk, (int, float)):
                    session['risk_score'] = max(session['risk_score'], event_risk)
                
                # Track event types
                event_type = event.get('event_type', '')
                if event_type:
                    session['event_types'].add(event_type)
        
        except Exception as e:
            self.logger.error(f"Error updating user sessions: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get engine statistics.
        
        Returns:
            Statistics dictionary
        """
        current_time = datetime.now()
        uptime = current_time - self.stats['start_time']
        
        stats = self.stats.copy()
        stats.update({
            'uptime_seconds': uptime.total_seconds(),
            'events_per_second': self.stats['events_processed'] / max(uptime.total_seconds(), 1),
            'queue_size': self.event_queue.qsize(),
            'active_user_sessions': len(self.user_sessions),
            'models_loaded': len([m for m in self.models.values() if m.is_trained])
        })
        
        return stats
    
    def get_user_session_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User session dictionary or None if not found
        """
        session = self.user_sessions.get(user_id)
        if session:
            # Convert set to list for JSON serialization
            session_copy = session.copy()
            session_copy['event_types'] = list(session_copy.get('event_types', []))
            return session_copy
        
        return None