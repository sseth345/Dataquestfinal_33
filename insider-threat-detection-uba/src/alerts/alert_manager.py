"""
Alert manager for handling, storing, and reporting on security alerts.
"""

import csv
import json
import logging
import sqlite3
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional, Callable
import os

import pandas as pd


class AlertManager:
    """
    Manages security alerts including storage, notifications, and reporting.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_path = config.get('database_path', 'data/threat_detection.db')
        
        # Alert callbacks
        self.alert_callbacks = []
        
        # Email configuration
        self.email_config = config.get('email', {})
        self.enable_email_alerts = self.email_config.get('enabled', False)
        
        # Initialize database
        self._init_alerts_database()
    
    def _init_alerts_database(self):
        """Initialize alerts database tables."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create alerts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        id TEXT PRIMARY KEY,
                        timestamp DATETIME NOT NULL,
                        severity TEXT NOT NULL,
                        status TEXT DEFAULT 'open',
                        user_id TEXT,
                        event_type TEXT,
                        anomaly_score REAL,
                        event_data TEXT,
                        detection_details TEXT,
                        user_context TEXT,
                        recommended_actions TEXT,
                        acknowledged_by TEXT,
                        acknowledged_at DATETIME,
                        notes TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create alert notifications table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alert_notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_id TEXT NOT NULL,
                        notification_type TEXT NOT NULL,
                        recipient TEXT NOT NULL,
                        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'sent',
                        error_message TEXT,
                        FOREIGN KEY (alert_id) REFERENCES alerts (id)
                    )
                ''')
                
                # Create indices for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id)')
                
                conn.commit()
                self.logger.info("Alerts database initialized successfully")
        
        except Exception as e:
            self.logger.error(f"Error initializing alerts database: {str(e)}")
    
    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Add a callback function that will be called when an alert is generated.
        
        Args:
            callback: Function that takes an alert dictionary as parameter
        """
        self.alert_callbacks.append(callback)
    
    def create_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Create and store a new alert.
        
        Args:
            alert: Alert dictionary containing alert information
            
        Returns:
            True if alert was created successfully, False otherwise
        """
        try:
            # Ensure required fields
            required_fields = ['id', 'timestamp', 'severity', 'anomaly_score']
            for field in required_fields:
                if field not in alert:
                    self.logger.error(f"Missing required field '{field}' in alert")
                    return False
            
            # Store alert in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO alerts (
                        id, timestamp, severity, user_id, event_type, 
                        anomaly_score, event_data, detection_details, 
                        user_context, recommended_actions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert['id'],
                    alert['timestamp'],
                    alert['severity'],
                    alert.get('event', {}).get('user_id'),
                    alert.get('event', {}).get('event_type'),
                    alert['anomaly_score'],
                    json.dumps(alert.get('event', {})),
                    json.dumps(alert.get('detection_details', {})),
                    json.dumps(alert.get('user_context', {})),
                    json.dumps(alert.get('recommended_actions', []))
                ))
                
                conn.commit()
            
            # Send notifications
            self._send_alert_notifications(alert)
            
            # Call registered callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"Error in alert callback: {str(e)}")
            
            self.logger.info(f"Alert created successfully: {alert['id']}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error creating alert: {str(e)}")
            return False
    
    def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific alert by ID.
        
        Args:
            alert_id: Alert identifier
            
        Returns:
            Alert dictionary or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM alerts WHERE id = ?
                ''', (alert_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    alert = dict(zip(columns, row))
                    
                    # Parse JSON fields
                    for field in ['event_data', 'detection_details', 'user_context', 'recommended_actions']:
                        if alert[field]:
                            try:
                                alert[field] = json.loads(alert[field])
                            except json.JSONDecodeError:
                                alert[field] = {}
                    
                    return alert
                
                return None
        
        except Exception as e:
            self.logger.error(f"Error getting alert {alert_id}: {str(e)}")
            return None
    
    def get_alerts(self, limit: int = 50, offset: int = 0, severity: str = None, 
                   status: str = None, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Get alerts with filtering and pagination.
        
        Args:
            limit: Maximum number of alerts to return
            offset: Number of alerts to skip
            severity: Filter by severity level
            status: Filter by status
            user_id: Filter by user ID
            
        Returns:
            List of alert dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM alerts WHERE 1=1"
                params = []
                
                if severity:
                    query += " AND severity = ?"
                    params.append(severity)
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)
                
                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                
                alerts = []
                for row in cursor.fetchall():
                    columns = [description[0] for description in cursor.description]
                    alert = dict(zip(columns, row))
                    
                    # Parse JSON fields
                    for field in ['event_data', 'detection_details', 'user_context', 'recommended_actions']:
                        if alert[field]:
                            try:
                                alert[field] = json.loads(alert[field])
                            except json.JSONDecodeError:
                                alert[field] = {}
                    
                    alerts.append(alert)
                
                return alerts
        
        except Exception as e:
            self.logger.error(f"Error getting alerts: {str(e)}")
            return []
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str, notes: str = "") -> bool:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: Alert identifier
            acknowledged_by: User who acknowledged the alert
            notes: Optional notes about the acknowledgment
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE alerts 
                    SET status = 'acknowledged', 
                        acknowledged_by = ?, 
                        acknowledged_at = ?, 
                        notes = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (acknowledged_by, datetime.now().isoformat(), notes, alert_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    self.logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
                    return True
                else:
                    self.logger.warning(f"Alert {alert_id} not found for acknowledgment")
                    return False
        
        except Exception as e:
            self.logger.error(f"Error acknowledging alert {alert_id}: {str(e)}")
            return False
    
    def close_alert(self, alert_id: str, closed_by: str, notes: str = "") -> bool:
        """
        Close an alert.
        
        Args:
            alert_id: Alert identifier
            closed_by: User who closed the alert
            notes: Optional notes about closing the alert
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE alerts 
                    SET status = 'closed', 
                        acknowledged_by = ?, 
                        acknowledged_at = ?, 
                        notes = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (closed_by, datetime.now().isoformat(), notes, alert_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    self.logger.info(f"Alert {alert_id} closed by {closed_by}")
                    return True
                else:
                    self.logger.warning(f"Alert {alert_id} not found for closing")
                    return False
        
        except Exception as e:
            self.logger.error(f"Error closing alert {alert_id}: {str(e)}")
            return False
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """
        Get alert statistics.
        
        Returns:
            Dictionary containing alert statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total alerts
                cursor.execute("SELECT COUNT(*) FROM alerts")
                stats['total_alerts'] = cursor.fetchone()[0]
                
                # Active alerts (open/acknowledged)
                cursor.execute("SELECT COUNT(*) FROM alerts WHERE status IN ('open', 'acknowledged')")
                stats['active_count'] = cursor.fetchone()[0]
                
                # Alerts by severity
                cursor.execute('''
                    SELECT severity, COUNT(*) 
                    FROM alerts 
                    WHERE status IN ('open', 'acknowledged')
                    GROUP BY severity
                ''')
                
                severity_counts = dict(cursor.fetchall())
                stats['high_severity_count'] = severity_counts.get('HIGH', 0)
                stats['medium_severity_count'] = severity_counts.get('MEDIUM', 0)
                stats['low_severity_count'] = severity_counts.get('LOW', 0)
                
                # Alerts by status
                cursor.execute('''
                    SELECT status, COUNT(*) 
                    FROM alerts 
                    GROUP BY status
                ''')
                
                status_counts = dict(cursor.fetchall())
                stats['open_count'] = status_counts.get('open', 0)
                stats['acknowledged_count'] = status_counts.get('acknowledged', 0)
                stats['closed_count'] = status_counts.get('closed', 0)
                
                # Recent alerts (last 24 hours)
                cursor.execute('''
                    SELECT COUNT(*) FROM alerts 
                    WHERE datetime(timestamp) > datetime('now', '-24 hours')
                ''')
                stats['alerts_last_24h'] = cursor.fetchone()[0]
                
                # Average response time (for acknowledged alerts)
                cursor.execute('''
                    SELECT AVG(
                        (julianday(acknowledged_at) - julianday(timestamp)) * 24 * 60
                    ) as avg_response_minutes
                    FROM alerts 
                    WHERE acknowledged_at IS NOT NULL
                ''')
                
                result = cursor.fetchone()[0]
                stats['avg_response_time_minutes'] = round(result or 0, 2)
                
                return stats
        
        except Exception as e:
            self.logger.error(f"Error getting alert statistics: {str(e)}")
            return {}
    
    def generate_csv_report(self, report_type: str = 'alerts', start_date: str = None, 
                           end_date: str = None) -> str:
        """
        Generate a CSV report of alerts.
        
        Args:
            report_type: Type of report ('alerts', 'summary')
            start_date: Start date for the report (ISO format)
            end_date: End date for the report (ISO format)
            
        Returns:
            Path to the generated CSV file
        """
        try:
            # Ensure reports directory exists
            reports_dir = 'reports'
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{report_type}_report_{timestamp}.csv"
            filepath = os.path.join(reports_dir, filename)
            
            if report_type == 'alerts':
                self._generate_alerts_csv_report(filepath, start_date, end_date)
            elif report_type == 'summary':
                self._generate_summary_csv_report(filepath, start_date, end_date)
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            self.logger.info(f"CSV report generated: {filepath}")
            return filepath
        
        except Exception as e:
            self.logger.error(f"Error generating CSV report: {str(e)}")
            raise
    
    def _generate_alerts_csv_report(self, filepath: str, start_date: str = None, 
                                   end_date: str = None):
        """Generate detailed alerts CSV report."""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT 
                    id, timestamp, severity, status, user_id, event_type,
                    anomaly_score, acknowledged_by, acknowledged_at, notes
                FROM alerts
                WHERE 1=1
            """
            
            params = []
            if start_date:
                query += " AND datetime(timestamp) >= datetime(?)"
                params.append(start_date)
            
            if end_date:
                query += " AND datetime(timestamp) <= datetime(?)"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC"
            
            df = pd.read_sql_query(query, conn, params=params)
            
            # Format timestamps
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            df['acknowledged_at'] = pd.to_datetime(df['acknowledged_at'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
            
            df.to_csv(filepath, index=False)
    
    def _generate_summary_csv_report(self, filepath: str, start_date: str = None, 
                                    end_date: str = None):
        """Generate summary CSV report."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build date filter
            date_filter = ""
            params = []
            if start_date:
                date_filter += " AND datetime(timestamp) >= datetime(?)"
                params.append(start_date)
            if end_date:
                date_filter += " AND datetime(timestamp) <= datetime(?)"
                params.append(end_date)
            
            # Get summary data
            summary_data = []
            
            # Alerts by severity
            cursor.execute(f'''
                SELECT severity, COUNT(*) as count, AVG(anomaly_score) as avg_score
                FROM alerts 
                WHERE 1=1 {date_filter}
                GROUP BY severity
            ''', params)
            
            for severity, count, avg_score in cursor.fetchall():
                summary_data.append({
                    'Category': 'Severity',
                    'Type': severity,
                    'Count': count,
                    'Average_Score': round(avg_score or 0, 3)
                })
            
            # Alerts by user
            cursor.execute(f'''
                SELECT user_id, COUNT(*) as count, AVG(anomaly_score) as avg_score
                FROM alerts 
                WHERE user_id IS NOT NULL {date_filter}
                GROUP BY user_id
                ORDER BY count DESC
                LIMIT 10
            ''', params)
            
            for user_id, count, avg_score in cursor.fetchall():
                summary_data.append({
                    'Category': 'User',
                    'Type': user_id,
                    'Count': count,
                    'Average_Score': round(avg_score or 0, 3)
                })
            
            # Alerts by event type
            cursor.execute(f'''
                SELECT event_type, COUNT(*) as count, AVG(anomaly_score) as avg_score
                FROM alerts 
                WHERE event_type IS NOT NULL {date_filter}
                GROUP BY event_type
                ORDER BY count DESC
            ''', params)
            
            for event_type, count, avg_score in cursor.fetchall():
                summary_data.append({
                    'Category': 'Event Type',
                    'Type': event_type,
                    'Count': count,
                    'Average_Score': round(avg_score or 0, 3)
                })
            
            # Write to CSV
            df = pd.DataFrame(summary_data)
            df.to_csv(filepath, index=False)
    
    def _send_alert_notifications(self, alert: Dict[str, Any]):
        """
        Send alert notifications via configured channels.
        
        Args:
            alert: Alert dictionary
        """
        try:
            # Send email notifications
            if self.enable_email_alerts and alert['severity'] in ['HIGH', 'MEDIUM']:
                self._send_email_notification(alert)
            
            # Add other notification methods here (Slack, Teams, etc.)
            
        except Exception as e:
            self.logger.error(f"Error sending alert notifications: {str(e)}")
    
    def _send_email_notification(self, alert: Dict[str, Any]):
        """
        Send email notification for an alert.
        
        Args:
            alert: Alert dictionary
        """
        try:
            if not self.email_config.get('smtp_server'):
                self.logger.warning("SMTP server not configured, skipping email notification")
                return
            
            # Create message
            msg = MimeMultipart()
            msg['From'] = self.email_config['from_email']
            msg['Subject'] = f"[{alert['severity']}] Insider Threat Alert - {alert['id']}"
            
            # Recipients
            recipients = self.email_config.get('recipients', [])
            if alert['severity'] == 'HIGH':
                recipients.extend(self.email_config.get('high_priority_recipients', []))
            
            if not recipients:
                self.logger.warning("No email recipients configured")
                return
            
            msg['To'] = ', '.join(recipients)
            
            # Email body
            body = self._format_alert_email(alert)
            msg.attach(MimeText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config.get('smtp_port', 587)) as server:
                if self.email_config.get('use_tls', True):
                    server.starttls()
                
                if self.email_config.get('username') and self.email_config.get('password'):
                    server.login(self.email_config['username'], self.email_config['password'])
                
                server.send_message(msg)
            
            # Log notification
            self._log_notification(alert['id'], 'email', recipients, 'sent')
            self.logger.info(f"Email notification sent for alert {alert['id']}")
        
        except Exception as e:
            self._log_notification(alert['id'], 'email', [], 'failed', str(e))
            self.logger.error(f"Error sending email notification: {str(e)}")
    
    def _format_alert_email(self, alert: Dict[str, Any]) -> str:
        """
        Format alert information for email notification.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            HTML formatted email body
        """
        severity_colors = {
            'HIGH': '#dc3545',
            'MEDIUM': '#fd7e14',
            'LOW': '#28a745'
        }
        
        color = severity_colors.get(alert['severity'], '#6c757d')
        
        html = f"""
        <html>
        <body>
            <h2 style="color: {color};">Insider Threat Alert</h2>
            
            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Alert ID:</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{alert['id']}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Severity:</td>
                    <td style="border: 1px solid #ddd; padding: 8px; color: {color}; font-weight: bold;">
                        {alert['severity']}
                    </td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Timestamp:</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{alert['timestamp']}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">User:</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">
                        {alert.get('event', {}).get('user_id', 'Unknown')}
                    </td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Event Type:</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">
                        {alert.get('event', {}).get('event_type', 'Unknown')}
                    </td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Anomaly Score:</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{alert['anomaly_score']:.3f}</td>
                </tr>
            </table>
            
            <h3>Recommended Actions:</h3>
            <ul>
        """
        
        for action in alert.get('recommended_actions', []):
            html += f"<li>{action}</li>"
        
        html += """
            </ul>
            
            <p><strong>Please investigate this alert immediately and take appropriate action.</strong></p>
            
            <p><em>This is an automated alert from the Insider Threat Detection System.</em></p>
        </body>
        </html>
        """
        
        return html
    
    def _log_notification(self, alert_id: str, notification_type: str, recipients: List[str], 
                         status: str, error_message: str = None):
        """
        Log notification attempt.
        
        Args:
            alert_id: Alert identifier
            notification_type: Type of notification
            recipients: List of recipients
            status: Notification status
            error_message: Error message if failed
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for recipient in recipients:
                    cursor.execute('''
                        INSERT INTO alert_notifications 
                        (alert_id, notification_type, recipient, status, error_message)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (alert_id, notification_type, recipient, status, error_message))
                
                conn.commit()
        
        except Exception as e:
            self.logger.error(f"Error logging notification: {str(e)}")
    
    def cleanup_old_alerts(self, days_to_keep: int = 90):
        """
        Clean up old closed alerts.
        
        Args:
            days_to_keep: Number of days to keep closed alerts
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                cursor.execute('''
                    DELETE FROM alert_notifications 
                    WHERE alert_id IN (
                        SELECT id FROM alerts 
                        WHERE status = 'closed' 
                        AND datetime(updated_at) < datetime(?)
                    )
                ''', (cutoff_date.isoformat(),))
                
                cursor.execute('''
                    DELETE FROM alerts 
                    WHERE status = 'closed' 
                    AND datetime(updated_at) < datetime(?)
                ''', (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                self.logger.info(f"Cleaned up {deleted_count} old alerts")
        
        except Exception as e:
            self.logger.error(f"Error cleaning up old alerts: {str(e)}")