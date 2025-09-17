"""
Main Flask web application for the insider threat detection dashboard.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sqlite3

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit

from real_time.data_processor import RealTimeDataProcessor
from alerts.alert_manager import AlertManager


class ThreatDetectionDashboard:
    """
    Web dashboard for insider threat detection visualization and management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize Flask app
        self.app = Flask(__name__, 
                        template_folder='templates',
                        static_folder='static')
        self.app.config['SECRET_KEY'] = config.get('secret_key', 'insider-threat-detection-key')
        
        # Initialize SocketIO for real-time updates
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize components
        self.data_processor = None
        self.alert_manager = None
        self.db_path = config.get('database_path', 'data/threat_detection.db')
        
        # Setup routes and socket handlers
        self._setup_routes()
        self._setup_socket_handlers()
        
    def initialize_components(self, data_processor: RealTimeDataProcessor, alert_manager: AlertManager):
        """
        Initialize the dashboard with required components.
        
        Args:
            data_processor: Real-time data processor instance
            alert_manager: Alert manager instance
        """
        self.data_processor = data_processor
        self.alert_manager = alert_manager
        
        # Setup alert callbacks for real-time updates
        if self.alert_manager:
            self.alert_manager.add_alert_callback(self._handle_new_alert)
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main dashboard page."""
            return render_template('dashboard.html')
        
        @self.app.route('/alerts')
        def alerts():
            """Alerts management page."""
            return render_template('alerts.html')
        
        @self.app.route('/users')
        def users():
            """User monitoring page."""
            return render_template('users.html')
        
        @self.app.route('/reports')
        def reports():
            """Reports page."""
            return render_template('reports.html')
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get system statistics."""
            try:
                stats = {}
                
                if self.data_processor:
                    stats['processor'] = self.data_processor.get_performance_stats()
                    stats['collectors'] = self.data_processor.get_collector_status()
                
                if self.alert_manager:
                    stats['alerts'] = self.alert_manager.get_alert_statistics()
                
                # Get database stats
                stats['database'] = self._get_database_stats()
                
                return jsonify(stats)
            
            except Exception as e:
                self.logger.error(f"Error getting stats: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/alerts')
        def get_alerts():
            """Get alerts with filtering and pagination."""
            try:
                # Get query parameters
                limit = int(request.args.get('limit', 50))
                offset = int(request.args.get('offset', 0))
                severity = request.args.get('severity')
                status = request.args.get('status')
                user_id = request.args.get('user_id')
                
                # Get alerts from alert manager
                if self.alert_manager:
                    alerts = self.alert_manager.get_alerts(
                        limit=limit,
                        offset=offset,
                        severity=severity,
                        status=status,
                        user_id=user_id
                    )
                else:
                    alerts = []
                
                return jsonify(alerts)
            
            except Exception as e:
                self.logger.error(f"Error getting alerts: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/alerts/<alert_id>', methods=['GET'])
        def get_alert(alert_id):
            """Get detailed information about a specific alert."""
            try:
                if self.alert_manager:
                    alert = self.alert_manager.get_alert(alert_id)
                    if alert:
                        return jsonify(alert)
                    else:
                        return jsonify({'error': 'Alert not found'}), 404
                else:
                    return jsonify({'error': 'Alert manager not available'}), 503
            
            except Exception as e:
                self.logger.error(f"Error getting alert {alert_id}: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
        def acknowledge_alert(alert_id):
            """Acknowledge an alert."""
            try:
                if self.alert_manager:
                    data = request.get_json() or {}
                    acknowledged_by = data.get('acknowledged_by', 'dashboard_user')
                    notes = data.get('notes', '')
                    
                    success = self.alert_manager.acknowledge_alert(alert_id, acknowledged_by, notes)
                    
                    if success:
                        # Emit real-time update
                        self.socketio.emit('alert_updated', {'alert_id': alert_id, 'status': 'acknowledged'})
                        return jsonify({'success': True})
                    else:
                        return jsonify({'error': 'Failed to acknowledge alert'}), 400
                else:
                    return jsonify({'error': 'Alert manager not available'}), 503
            
            except Exception as e:
                self.logger.error(f"Error acknowledging alert {alert_id}: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/users')
        def get_users():
            """Get user information and activity."""
            try:
                users = self._get_user_data()
                return jsonify(users)
            
            except Exception as e:
                self.logger.error(f"Error getting users: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/users/<user_id>')
        def get_user(user_id):
            """Get detailed information about a specific user."""
            try:
                user_data = self._get_user_details(user_id)
                return jsonify(user_data)
            
            except Exception as e:
                self.logger.error(f"Error getting user {user_id}: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/events')
        def get_events():
            """Get recent events with filtering."""
            try:
                limit = int(request.args.get('limit', 100))
                event_type = request.args.get('event_type')
                user_id = request.args.get('user_id')
                
                events = self._get_events(limit=limit, event_type=event_type, user_id=user_id)
                return jsonify(events)
            
            except Exception as e:
                self.logger.error(f"Error getting events: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/reports/generate', methods=['POST'])
        def generate_report():
            """Generate a CSV report."""
            try:
                data = request.get_json()
                report_type = data.get('type', 'alerts')
                start_date = data.get('start_date')
                end_date = data.get('end_date')
                
                if self.alert_manager:
                    report_path = self.alert_manager.generate_csv_report(
                        report_type=report_type,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    return jsonify({'report_path': report_path, 'success': True})
                else:
                    return jsonify({'error': 'Alert manager not available'}), 503
            
            except Exception as e:
                self.logger.error(f"Error generating report: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/force-collection', methods=['POST'])
        def force_collection():
            """Force immediate data collection."""
            try:
                data = request.get_json() or {}
                collector_name = data.get('collector')
                
                if self.data_processor:
                    self.data_processor.force_collection(collector_name)
                    return jsonify({'success': True})
                else:
                    return jsonify({'error': 'Data processor not available'}), 503
            
            except Exception as e:
                self.logger.error(f"Error forcing collection: {str(e)}")
                return jsonify({'error': str(e)}), 500
    
    def _setup_socket_handlers(self):
        """Setup SocketIO event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            self.logger.info(f"Client connected: {request.sid}")
            emit('connected', {'data': 'Connected to threat detection dashboard'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            self.logger.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('subscribe_alerts')
        def handle_subscribe_alerts():
            """Subscribe client to alert updates."""
            # Client will receive real-time alert updates
            emit('subscribed', {'channel': 'alerts'})
        
        @self.socketio.on('subscribe_stats')
        def handle_subscribe_stats():
            """Subscribe client to statistics updates."""
            # Client will receive real-time stats updates
            emit('subscribed', {'channel': 'stats'})
    
    def _handle_new_alert(self, alert: Dict[str, Any]):
        """
        Handle new alerts for real-time updates.
        
        Args:
            alert: Alert dictionary
        """
        try:
            # Emit alert to all connected clients
            self.socketio.emit('new_alert', alert)
            self.logger.debug(f"Emitted new alert: {alert['id']}")
        
        except Exception as e:
            self.logger.error(f"Error emitting new alert: {str(e)}")
    
    def _get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Get table counts
                tables = ['user_events', 'anomalies', 'user_profiles']
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        stats[f"{table}_count"] = count
                    except sqlite3.OperationalError:
                        stats[f"{table}_count"] = 0
                
                # Get recent activity
                cursor.execute("""
                    SELECT COUNT(*) FROM user_events 
                    WHERE datetime(created_at) > datetime('now', '-24 hours')
                """)
                stats['events_last_24h'] = cursor.fetchone()[0]
                
                return stats
        
        except Exception as e:
            self.logger.error(f"Error getting database stats: {str(e)}")
            return {}
    
    def _get_user_data(self) -> List[Dict[str, Any]]:
        """Get user data for the dashboard."""
        try:
            users = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get users with recent activity
                cursor.execute("""
                    SELECT 
                        user_id,
                        COUNT(*) as event_count,
                        MAX(timestamp) as last_activity,
                        AVG(risk_score) as avg_risk_score
                    FROM user_events 
                    WHERE datetime(timestamp) > datetime('now', '-7 days')
                    GROUP BY user_id
                    ORDER BY avg_risk_score DESC, event_count DESC
                    LIMIT 50
                """)
                
                for row in cursor.fetchall():
                    user_id, event_count, last_activity, avg_risk_score = row
                    
                    # Get session info if available
                    session_info = {}
                    if self.data_processor and self.data_processor.anomaly_engine:
                        session_info = self.data_processor.anomaly_engine.get_user_session_info(user_id) or {}
                    
                    users.append({
                        'user_id': user_id,
                        'event_count': event_count,
                        'last_activity': last_activity,
                        'avg_risk_score': round(avg_risk_score or 0, 3),
                        'session_info': session_info
                    })
            
            return users
        
        except Exception as e:
            self.logger.error(f"Error getting user data: {str(e)}")
            return []
    
    def _get_user_details(self, user_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific user."""
        try:
            user_details = {'user_id': user_id}
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get recent events
                cursor.execute("""
                    SELECT event_type, timestamp, risk_score, event_data
                    FROM user_events 
                    WHERE user_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT 50
                """, (user_id,))
                
                events = []
                for row in cursor.fetchall():
                    event_type, timestamp, risk_score, event_data = row
                    events.append({
                        'event_type': event_type,
                        'timestamp': timestamp,
                        'risk_score': risk_score,
                        'event_data': json.loads(event_data) if event_data else {}
                    })
                
                user_details['recent_events'] = events
                
                # Get user profile
                cursor.execute("""
                    SELECT * FROM user_profiles WHERE user_id = ?
                """, (user_id,))
                
                profile_row = cursor.fetchone()
                if profile_row:
                    columns = [description[0] for description in cursor.description]
                    profile = dict(zip(columns, profile_row))
                    user_details['profile'] = profile
                
                # Get session info
                if self.data_processor and self.data_processor.anomaly_engine:
                    session_info = self.data_processor.anomaly_engine.get_user_session_info(user_id)
                    if session_info:
                        user_details['session'] = session_info
            
            return user_details
        
        except Exception as e:
            self.logger.error(f"Error getting user details for {user_id}: {str(e)}")
            return {'user_id': user_id, 'error': str(e)}
    
    def _get_events(self, limit: int = 100, event_type: str = None, user_id: str = None) -> List[Dict[str, Any]]:
        """Get recent events with optional filtering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT user_id, event_type, timestamp, source_ip, 
                           machine_name, risk_score, event_data
                    FROM user_events
                    WHERE 1=1
                """
                params = []
                
                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type)
                
                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                
                events = []
                for row in cursor.fetchall():
                    user_id, event_type, timestamp, source_ip, machine_name, risk_score, event_data = row
                    
                    events.append({
                        'user_id': user_id,
                        'event_type': event_type,
                        'timestamp': timestamp,
                        'source_ip': source_ip,
                        'machine_name': machine_name,
                        'risk_score': risk_score,
                        'event_data': json.loads(event_data) if event_data else {}
                    })
                
                return events
        
        except Exception as e:
            self.logger.error(f"Error getting events: {str(e)}")
            return []
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """
        Run the dashboard web application.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Enable debug mode
        """
        self.logger.info(f"Starting dashboard on {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)


def create_dashboard_app(config: Dict[str, Any]) -> ThreatDetectionDashboard:
    """
    Create and configure the dashboard application.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured dashboard instance
    """
    return ThreatDetectionDashboard(config)