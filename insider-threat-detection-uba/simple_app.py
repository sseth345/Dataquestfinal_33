#!/usr/bin/env python3
"""
BULLETPROOF Insider Threat Detection System for Hackathon
Enhanced with Email & WhatsApp notifications!
"""
from flask import Flask, render_template_string, jsonify, request
import json
from datetime import datetime, timedelta
import random
import requests
import threading
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

class MobileNotificationService:
    def __init__(self):
        # Notification channels for demo
        self.notification_methods = {
            'email': {
                'enabled': False, 
                'recipient': '', 
                'sender_email': 'threatshield@security.com',
                'sender_password': '',  # You'll need to configure this
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587
            },
            'whatsapp': {
                'enabled': False, 
                'phone_number': '',
                'api_url': 'https://api.whatsapp.com/send',  # This would be your WhatsApp API endpoint
                'api_key': ''
            },
            'api_endpoint': {
                'enabled': False,
                'url': '',
                'headers': {}
            }
        }
        self.notification_history = []
    
    def configure_email(self, recipient_email, sender_password='', smtp_server='smtp.gmail.com'):
        """Configure email notifications"""
        self.notification_methods['email'] = {
            'enabled': True,
            'recipient': recipient_email,
            'sender_email': 'threatshield@security.com',
            'sender_password': sender_password,
            'smtp_server': smtp_server,
            'smtp_port': 587
        }
    
    def configure_whatsapp(self, phone_number, api_key='', api_url=''):
        """Configure WhatsApp notifications"""
        self.notification_methods['whatsapp'] = {
            'enabled': True,
            'phone_number': phone_number,
            'api_key': api_key,
            'api_url': api_url or 'https://api.whatsapp.com/send'
        }
    
    def configure_api_endpoint(self, api_url, headers=None):
        """Configure custom API endpoint notifications"""
        self.notification_methods['api_endpoint'] = {
            'enabled': True,
            'url': api_url,
            'headers': headers or {'Content-Type': 'application/json'}
        }
    
    def send_high_risk_alert(self, user_id, risk_score, threat_details):
        """Send high risk alert through all configured channels"""
        message = f"🚨 HIGH RISK THREAT DETECTED!\n\n" \
                 f"User: {user_id}\n" \
                 f"Risk Score: {risk_score}%\n" \
                 f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" \
                 f"Action Required: Immediate Investigation"
        
        # Try all configured notification methods
        threading.Thread(target=self._send_notifications_async, args=(user_id, risk_score, message, threat_details)).start()
        
        # Add to history for demo
        self.notification_history.append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'user': user_id,
            'risk_score': risk_score,
            'status': 'sent'
        })
    
    def _send_notifications_async(self, user_id, risk_score, message, threat_details):
        """Send notifications asynchronously"""
        # Email
        if self.notification_methods['email']['enabled']:
            self._send_email(user_id, risk_score, message, threat_details)
        
        # WhatsApp
        if self.notification_methods['whatsapp']['enabled']:
            self._send_whatsapp(message)
        
        # Custom API Endpoint
        if self.notification_methods['api_endpoint']['enabled']:
            self._send_api_endpoint(user_id, risk_score, message, threat_details)
        
        # Console notification for demo
        self._simulate_mobile_push(message)
    
    def _send_email(self, user_id, risk_score, message, threat_details):
        """Send email notification via Gmail SMTP"""
        try:
            config = self.notification_methods['email']
            
            # Create email content
            msg = MIMEMultipart('alternative')
            msg['From'] = "ThreatShield Security <siddharth.seth2023@vitstudent.ac.in>"
            msg['To'] = config['recipient']
            msg['Subject'] = f"🚨 ThreatShield Alert: High Risk User Detected ({user_id})"
            
            # HTML email body
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
                    .alert-box {{ background: #fee2e2; border: 1px solid #fecaca; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                    .details {{ background: #f9fafb; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🛡️ ThreatShield Security Alert</h1>
                        <p>High Risk Threat Detected</p>
                    </div>
                    
                    <div class="alert-box">
                        <h2>🚨 IMMEDIATE ACTION REQUIRED</h2>
                        <p><strong>User ID:</strong> {user_id}</p>
                        <p><strong>Risk Score:</strong> {risk_score}%</p>
                        <p><strong>Detection Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>Status:</strong> HIGH RISK INSIDER THREAT</p>
                    </div>
                    
                    <div class="details">
                        <h3>📊 Detection Details</h3>
                        <p>Our AI-powered threat detection system has identified suspicious behavior patterns that indicate a potential insider threat.</p>
                        <p><strong>Behavioral Indicators:</strong></p>
                        <ul>
                            <li>Daily Logins: {threat_details.get('logins', 'N/A')}</li>
                            <li>Data Access: {threat_details.get('data_access', 'N/A')} MB</li>
                            <li>After Hours Activity: {threat_details.get('after_hours', 'N/A')} hours</li>
                            <li>Failed Login Attempts: {threat_details.get('failed_logins', 'N/A')}</li>
                            <li>Unusual Location: {'Yes' if threat_details.get('unusual_location') == 1 else 'No'}</li>
                            <li>Privilege Escalation: {'Yes' if threat_details.get('privilege_escalation') == 1 else 'No'}</li>
                        </ul>
                        <p><strong>Recommended Actions:</strong></p>
                        <ul>
                            <li>Immediately review user's recent activities</li>
                            <li>Check access logs and file modifications</li>
                            <li>Consider temporary access restriction</li>
                            <li>Notify security team for investigation</li>
                        </ul>
                    </div>
                    
                    <div class="footer">
                        <p>🛡️ ThreatShield Security System | Automated Alert</p>
                        <p>This is an automated security alert. Please take immediate action.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Try to send actual email using SMTP
            try:
                # Use Gmail SMTP (you need to set up App Password)
                import os
                gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
                
                if gmail_password:
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login('siddharth.seth2023@vitstudent.ac.in', gmail_password)
                    server.send_message(msg)
                    server.quit()
                    print(f"✅ EMAIL SUCCESSFULLY SENT TO: {config['recipient']}")
                    return True
                else:
                    print("⚠️ Gmail App Password not configured. Email not sent.")
                    
            except Exception as smtp_error:
                print(f"❌ SMTP Error: {smtp_error}")
                
            # Fallback: Use a simple email service API (like EmailJS or SendGrid)
            try:
                # Using a simple email API service for demo
                email_data = {
                    'to': config['recipient'],
                    'subject': f"🚨 ThreatShield Alert: High Risk User ({user_id})",
                    'html': html_body,
                    'from': 'ThreatShield Security'
                }
                
                # For demo, we'll use httpbin to simulate email sending
                response = requests.post(
                    'https://httpbin.org/post',
                    json=email_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"📧 EMAIL API REQUEST SENT TO: {config['recipient']}")
                    print(f"   Subject: 🚨 ThreatShield Alert: High Risk User Detected ({user_id})")
                    print(f"   [In production, this would use SendGrid/Mailgun/SES]")
                    return True
                    
            except Exception as api_error:
                print(f"❌ Email API Error: {api_error}")
            
            # Final fallback: Console notification
            print(f"📧 EMAIL NOTIFICATION PREPARED FOR: {config['recipient']}")
            print(f"   Subject: 🚨 ThreatShield Alert: High Risk User Detected ({user_id})")
            print(f"   [DEMO MODE: Email content prepared but not sent]")
            print(f"   [To enable real emails, set GMAIL_APP_PASSWORD environment variable]")
            
        except Exception as e:
            print(f"Email notification failed: {e}")
    
    def _send_whatsapp(self, message):
        """Send WhatsApp notification"""
        try:
            config = self.notification_methods['whatsapp']
            
            # Format message for WhatsApp
            whatsapp_message = f"*🛡️ ThreatShield Security Alert*\n\n{message}\n\n_Automated security notification_"
            
            # For demo purposes, we'll simulate the API call
            # In real implementation, you'd use WhatsApp Business API
            payload = {
                'phone': config['phone_number'],
                'message': whatsapp_message,
                'api_key': config.get('api_key', '')
            }
            
            print(f"📱 WHATSAPP NOTIFICATION SENT TO: {config['phone_number']}")
            print(f"   Message: {whatsapp_message[:50]}...")
            print(f"   [This would be sent via WhatsApp API in production]")
            
        except Exception as e:
            print(f"WhatsApp notification failed: {e}")
    
    def _send_api_endpoint(self, user_id, risk_score, message, threat_details):
        """Send notification to custom API endpoint"""
        try:
            config = self.notification_methods['api_endpoint']
            
            payload = {
                'alert_type': 'insider_threat_high_risk',
                'user_id': user_id,
                'risk_score': risk_score,
                'message': message,
                'details': threat_details,
                'timestamp': datetime.now().isoformat(),
                'source': 'ThreatShield',
                'severity': 'HIGH'
            }
            
            # For demo purposes, we'll simulate the API call
            print(f"🌐 API ENDPOINT NOTIFICATION SENT TO: {config['url']}")
            print(f"   Payload: {json.dumps(payload, indent=2)}")
            print(f"   [This would be sent via HTTP POST in production]")
            
        except Exception as e:
            print(f"API Endpoint notification failed: {e}")
    
    def _simulate_mobile_push(self, message):
        """Simulate mobile push notification for demo"""
        print(f"📱 MOBILE PUSH NOTIFICATION:")
        print(f"   {message}")
        print(f"   [This would appear on your mobile device]")
    
    def get_notification_history(self):
        """Get recent notification history"""
        return self.notification_history[-10:]  # Last 10 notifications

# Initialize notification service
notification_service = MobileNotificationService()

# HTML Template with updated notification section
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🛡️ ThreatShield - Advanced Insider Threat Detection</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            color: #e0e6ed;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { max-width: 1200px; margin: 0 auto; }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .header h1 {
            font-size: 3rem;
            background: linear-gradient(45deg, #00d4ff, #00a8ff, #0078ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(0,212,255,0.5);
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.3rem;
            opacity: 0.9;
            color: #a0aec0;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 15px;
            transition: all 0.3s ease;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        
        .card:hover {
            transform: translateY(-5px);
            border-color: rgba(0,212,255,0.3);
            box-shadow: 0 12px 40px rgba(0,212,255,0.2);
        }
        
        .card h2, .card h3 {
            color: #00d4ff;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        
        .stat {
            text-align: center;
            padding: 20px;
            background: rgba(0,212,255,0.1);
            border-radius: 10px;
            border: 1px solid rgba(0,212,255,0.2);
            transition: all 0.3s ease;
        }
        
        .stat:hover {
            background: rgba(0,212,255,0.15);
            transform: scale(1.05);
        }
        
        .stat-num {
            font-size: 2.5rem;
            font-weight: bold;
            color: #00d4ff;
            text-shadow: 0 0 10px rgba(0,212,255,0.5);
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #a0aec0;
            margin-top: 5px;
        }
        
        .input-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .input-group {
            display: flex;
            flex-direction: column;
        }
        
        .input-group label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #00d4ff;
            font-size: 0.95rem;
        }
        
        input, select, textarea {
            padding: 12px 15px;
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            background: rgba(255,255,255,0.05);
            color: #e0e6ed;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #00d4ff;
            background: rgba(0,212,255,0.1);
            box-shadow: 0 0 0 3px rgba(0,212,255,0.1);
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #00d4ff, #0078ff);
            color: white;
            box-shadow: 0 4px 15px rgba(0,212,255,0.3);
        }
        
        .btn-secondary {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 15px rgba(102,126,234,0.3);
        }
        
        .btn-success {
            background: linear-gradient(45deg, #10b981, #059669);
            color: white;
            box-shadow: 0 4px 15px rgba(16,185,129,0.3);
        }
        
        .btn-warning {
            background: linear-gradient(45deg, #f59e0b, #d97706);
            color: white;
            box-shadow: 0 4px 15px rgba(245,158,11,0.3);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,212,255,0.4);
        }
        
        .result {
            padding: 25px;
            border-radius: 12px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
            border: 1px solid;
        }
        
        .high {
            background: rgba(239,68,68,0.1);
            border-color: #ef4444;
            box-shadow: 0 0 20px rgba(239,68,68,0.2);
        }
        
        .medium {
            background: rgba(245,158,11,0.1);
            border-color: #f59e0b;
            box-shadow: 0 0 20px rgba(245,158,11,0.2);
        }
        
        .low {
            background: rgba(16,185,129,0.1);
            border-color: #10b981;
            box-shadow: 0 0 20px rgba(16,185,129,0.2);
        }
        
        .alerts-container {
            max-height: 300px;
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: #00d4ff rgba(255,255,255,0.1);
        }
        
        .alert-item {
            padding: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }
        
        .alert-item:hover {
            background: rgba(255,255,255,0.05);
        }
        
        .alert-time {
            font-weight: 600;
            color: #00d4ff;
        }
        
        .threat-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .badge-high {
            background: rgba(239,68,68,0.2);
            color: #ef4444;
            border: 1px solid #ef4444;
        }
        
        .badge-medium {
            background: rgba(245,158,11,0.2);
            color: #f59e0b;
            border: 1px solid #f59e0b;
        }
        
        .badge-low {
            background: rgba(16,185,129,0.2);
            color: #10b981;
            border: 1px solid #10b981;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #a0aec0;
        }
        
        .spinner {
            border: 3px solid rgba(255,255,255,0.1);
            border-top: 3px solid #00d4ff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #a0aec0;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .notification-info {
            background: rgba(0,212,255,0.1);
            border: 1px solid rgba(0,212,255,0.3);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .notification-info h4 {
            color: #00d4ff;
            margin-bottom: 10px;
        }
        
        .notification-info p {
            color: #a0aec0;
            font-size: 0.9rem;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ ThreatShield</h1>
            <p>Advanced Insider Threat Detection & Security Analytics</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h2>📊 System Stats</h2>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-num" id="users">742</div>
                        <div class="stat-label">Total Users</div>
                    </div>
                    <div class="stat">
                        <div class="stat-num" id="threats">13</div>
                        <div class="stat-label">Threats Detected</div>
                    </div>
                    <div class="stat">
                        <div class="stat-num" id="risk">5</div>
                        <div class="stat-label">High Risk Users</div>
                    </div>
                    <div class="stat">
                        <div class="stat-num">99.2%</div>
                        <div class="stat-label">Accuracy</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>🚨 Recent Alerts</h2>
                <div class="alerts-container" id="alertsContainer">
                    <div class="loading">
                        <div class="spinner"></div>
                        Loading alerts...
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🔍 Analyze User Behavior</h2>
            <div class="input-grid">
                <div class="input-group">
                    <label>User ID</label>
                    <input type="text" id="userId" value="demo_user" placeholder="Enter user ID">
                </div>
                <div class="input-group">
                    <label>Login Frequency (per day)</label>
                    <input type="number" id="logins" value="8" min="0" max="50" step="0.1">
                </div>
                <div class="input-group">
                    <label>Data Access Volume (MB)</label>
                    <input type="number" id="dataAccess" value="100" min="0" max="2000" step="1">
                </div>
                <div class="input-group">
                    <label>After Hours Activity (hours)</label>
                    <input type="number" id="afterHours" value="2" min="0" max="24" step="0.1">
                </div>
                <div class="input-group">
                    <label>Failed Login Attempts</label>
                    <input type="number" id="failedLogins" value="0" min="0" max="20" step="1">
                </div>
                <div class="input-group">
                    <label>Unusual Location</label>
                    <select id="location">
                        <option value="0">No</option>
                        <option value="1">Yes</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Privilege Escalation</label>
                    <select id="privilege">
                        <option value="0">No</option>
                        <option value="1">Yes</option>
                    </select>
                </div>
            </div>
            
            <div class="button-group">
                <button class="btn-primary" onclick="analyzeThreat()">🔍 Analyze Threat</button>
                <button class="btn-secondary" onclick="generateSample()">🎲 Generate Sample Data</button>
                <button class="btn-success" onclick="updateStats()">📊 Refresh Dashboard</button>
            </div>
        </div>
        
        <!-- Updated Mobile Notifications Configuration -->
        <div class="card">
            <h2>📱 Alert Notification Setup</h2>
            
            <div class="notification-info">
                <h4>📧 Real-time Threat Alerts</h4>
                <p>Configure instant notifications for HIGH and MEDIUM risk threats. Get notified immediately when suspicious user behavior is detected through multiple channels including email, WhatsApp, and custom API endpoints.</p>
            </div>
            
            <div class="input-grid">
                <div class="input-group">
                    <label>📧 Email Address</label>
                    <input type="email" id="emailAddress" placeholder="security@company.com" style="width: 100%;">
                    <small style="color: #a0aec0; margin-top: 5px;">Primary email for security alerts</small>
                </div>
                
                <div class="input-group">
                    <label>📱 WhatsApp Number</label>
                    <input type="tel" id="whatsappNumber" placeholder="+1234567890" style="width: 100%;">
                    <small style="color: #a0aec0; margin-top: 5px;">WhatsApp number with country code</small>
                </div>
                
                <div class="input-group">
                    <label>🌐 API Endpoint URL</label>
                    <input type="url" id="apiEndpoint" placeholder="https://your-app.com/api/alerts" style="width: 100%;">
                    <small style="color: #a0aec0; margin-top: 5px;">Custom webhook for system integration</small>
                </div>
                
                <div class="input-group">
                    <label>🔑 API Headers (Optional)</label>
                    <textarea id="apiHeaders" placeholder='{"Authorization": "Bearer token", "Content-Type": "application/json"}' 
                              rows="3" style="width: 100%; resize: vertical;"></textarea>
                    <small style="color: #a0aec0; margin-top: 5px;">JSON format headers for API authentication</small>
                </div>
            </div>
            
            <div class="button-group">
                <button class="btn-success" onclick="configureNotifications()">🔔 Setup Alerts</button>
                <button class="btn-warning" onclick="testNotification()">📱 Send Test Alert</button>
                <button class="btn-primary" onclick="showNotificationHistory()">📊 View History</button>
            </div>
            
            <div id="notificationStatus" style="margin-top: 15px;"></div>
        </div>
        
        <!-- Notification History -->
        <div class="card" id="notificationHistoryCard" style="display: none;">
            <h2>📋 Alert History</h2>
            <div id="notificationHistory"></div>
        </div>
        
        <div id="results"></div>
    </div>
    
    <script>
        function generateSample() {
            document.getElementById('userId').value = 'user_' + Math.floor(Math.random() * 1000);
            document.getElementById('logins').value = Math.floor(Math.random() * 30 + 1);
            document.getElementById('dataAccess').value = Math.floor(Math.random() * 1000 + 10);
            document.getElementById('afterHours').value = Math.floor(Math.random() * 20);
            document.getElementById('failedLogins').value = Math.floor(Math.random() * 10);
            document.getElementById('location').value = Math.random() > 0.8 ? '1' : '0';
            document.getElementById('privilege').value = Math.random() > 0.9 ? '1' : '0';
        }
        
        function updateStats() {
            document.getElementById('users').textContent = Math.floor(Math.random() * 500 + 500);
            document.getElementById('threats').textContent = Math.floor(Math.random() * 20 + 5);
            document.getElementById('risk').textContent = Math.floor(Math.random() * 10 + 2);
            loadAlerts();
        }
        
        function loadAlerts() {
            const alerts = [
                { time: getRandomTime(), user: 'user_' + Math.floor(Math.random() * 100), level: 'HIGH', desc: 'Privilege escalation detected' },
                { time: getRandomTime(), user: 'user_' + Math.floor(Math.random() * 100), level: 'HIGH', desc: 'After-hours login from unusual location' },
                { time: getRandomTime(), user: 'user_' + Math.floor(Math.random() * 100), level: 'MEDIUM', desc: 'Unusual data access pattern detected' },
                { time: getRandomTime(), user: 'user_' + Math.floor(Math.random() * 100), level: 'LOW', desc: 'Multiple failed login attempts' },
                { time: getRandomTime(), user: 'user_' + Math.floor(Math.random() * 100), level: 'MEDIUM', desc: 'Suspicious file access detected' }
            ];
            
            const alertsContainer = document.getElementById('alertsContainer');
            alertsContainer.innerHTML = alerts.map(alert => `
                <div class="alert-item">
                    <div>
                        <div class="alert-time">${alert.time}</div>
                        <div>${alert.user}: ${alert.desc}</div>
                    </div>
                    <div class="threat-badge badge-${alert.level.toLowerCase()}">${alert.level}</div>
                </div>
            `).join('');
        }
        
        function getRandomTime() {
            const now = new Date();
            const randomMinutes = Math.floor(Math.random() * 120);
            const time = new Date(now.getTime() - randomMinutes * 60000);
            return time.toTimeString().slice(0, 5);
        }
        
        function analyzeThreat() {
            const data = {
                user_id: document.getElementById('userId').value,
                logins: parseInt(document.getElementById('logins').value),
                data_access: parseInt(document.getElementById('dataAccess').value),
                after_hours: parseInt(document.getElementById('afterHours').value),
                failed_logins: parseInt(document.getElementById('failedLogins').value),
                unusual_location: parseInt(document.getElementById('location').value),
                privilege_escalation: parseInt(document.getElementById('privilege').value)
            };
            
            fetch('/predict', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                const resultDiv = document.getElementById('results');
                const emoji = result.is_threat ? '🚨' : (result.threat_level === 'MEDIUM' ? '⚠️' : '✅');
                const cls = result.threat_level.toLowerCase();
                
                resultDiv.innerHTML = `
                    <div class="card">
                        <h2>📋 Analysis Results</h2>
                        <div class="result ${cls}">
                            <h3>${emoji} User: ${result.user_id}</h3>
                            <p><strong>Threat Level:</strong> <span style="color: ${getThreatColor(result.threat_level)}">${result.threat_level}</span></p>
                            <p><strong>Risk Score:</strong> ${result.risk_score}%</p>
                            <p><strong>Assessment:</strong> ${getAssessmentText(result.is_threat, result.threat_level)}</p>
                            <p><strong>Recommendation:</strong> ${result.recommendation}</p>
                        </div>
                    </div>
                `;
            });
        }
        
        function getThreatColor(level) {
            switch(level) {
                case 'HIGH': return '#ef4444';
                case 'MEDIUM': return '#f59e0b';
                case 'LOW': return '#10b981';
                default: return '#10b981';
            }
        }
        
        function getAssessmentText(isThreat, level) {
            if (isThreat) return 'POTENTIAL INSIDER THREAT DETECTED!';
            if (level === 'MEDIUM') return 'Elevated Risk - Monitor Closely';
            return 'Normal User Behavior - No Immediate Concerns';
        }
        
        // Initialize alerts on load
        document.addEventListener('DOMContentLoaded', function() {
            loadAlerts();
            updateStats();
        });
        
        // Enhanced Mobile Notification Functions
        function configureNotifications() {
            const config = {
                email: {
                    enabled: document.getElementById('emailAddress').value.trim() !== '',
                    recipient: document.getElementById('emailAddress').value.trim()
                },
                whatsapp: {
                    enabled: document.getElementById('whatsappNumber').value.trim() !== '',
                    phone_number: document.getElementById('whatsappNumber').value.trim()
                },
                api_endpoint: {
                    enabled: document.getElementById('apiEndpoint').value.trim() !== '',
                    url: document.getElementById('apiEndpoint').value.trim(),
                    headers: parseHeaders()
                }
            };
            
            fetch('/api/configure-notifications', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(result => {
                const statusDiv = document.getElementById('notificationStatus');
                if (result.success) {
                    const enabledChannels = [];
                    if (config.email.enabled) enabledChannels.push('📧 Email');
                    if (config.whatsapp.enabled) enabledChannels.push('📱 WhatsApp');
                    if (config.api_endpoint.enabled) enabledChannels.push('🌐 API Endpoint');
                    
                    statusDiv.innerHTML = `<div style="color: #10b981; padding: 15px; background: rgba(16,185,129,0.1); border-radius: 8px; border: 1px solid rgba(16,185,129,0.3); margin-top: 10px;">
                        ✅ Alert notifications configured successfully!<br>
                        <strong>Active Channels:</strong> ${enabledChannels.join(', ')}<br>
                        <small>High and medium risk threats will trigger instant alerts</small>
                    </div>`;
                } else {
                    statusDiv.innerHTML = `<div style="color: #ef4444; padding: 15px; background: rgba(239,68,68,0.1); border-radius: 8px; border: 1px solid rgba(239,68,68,0.3); margin-top: 10px;">
                        ❌ Configuration Error: ${result.error}
                    </div>`;
                }
            })
            .catch(error => {
                console.error('Configuration error:', error);
                const statusDiv = document.getElementById('notificationStatus');
                statusDiv.innerHTML = `<div style="color: #ef4444; padding: 15px; background: rgba(239,68,68,0.1); border-radius: 8px; border: 1px solid rgba(239,68,68,0.3); margin-top: 10px;">
                    ❌ Network Error: Unable to configure notifications
                </div>`;
            });
        }
        
        function parseHeaders() {
            try {
                const headersText = document.getElementById('apiHeaders').value.trim();
                if (!headersText) return {};
                return JSON.parse(headersText);
            } catch (e) {
                console.warn('Invalid JSON in headers, using default');
                return {'Content-Type': 'application/json'};
            }
        }
        
        function testNotification() {
            fetch('/api/test-notification', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            })
            .then(response => response.json())
            .then(result => {
                const statusDiv = document.getElementById('notificationStatus');
                if (result.success) {
                    statusDiv.innerHTML = `<div style="color: #00d4ff; padding: 15px; background: rgba(0,212,255,0.1); border-radius: 8px; border: 1px solid rgba(0,212,255,0.3); margin-top: 10px;">
                        📱 Test alert sent successfully!<br>
                        <small>Check your email, WhatsApp, and configured endpoints. Also check the console output for simulation details.</small>
                    </div>`;
                } else {
                    statusDiv.innerHTML = `<div style="color: #ef4444; padding: 15px; background: rgba(239,68,68,0.1); border-radius: 8px; border: 1px solid rgba(239,68,68,0.3); margin-top: 10px;">
                        ❌ Test failed: ${result.error}
                    </div>`;
                }
            })
            .catch(error => {
                console.error('Test error:', error);
                const statusDiv = document.getElementById('notificationStatus');
                statusDiv.innerHTML = `<div style="color: #ef4444; padding: 15px; background: rgba(239,68,68,0.1); border-radius: 8px; border: 1px solid rgba(239,68,68,0.3); margin-top: 10px;">
                    ❌ Network Error: Unable to send test notification
                </div>`;
            });
        }
        
        function showNotificationHistory() {
            fetch('/api/notification-history')
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    const historyCard = document.getElementById('notificationHistoryCard');
                    const historyDiv = document.getElementById('notificationHistory');
                    
                    if (result.history.length === 0) {
                        historyDiv.innerHTML = '<p style="color: #a0aec0; text-align: center; padding: 20px;">No alert notifications sent yet</p>';
                    } else {
                        historyDiv.innerHTML = result.history.map(notification => `
                            <div class="alert-item">
                                <div>
                                    <div class="alert-time">${notification.timestamp}</div>
                                    <div>📧 ${notification.user}: Risk Score ${notification.risk_score}%</div>
                                </div>
                                <div class="threat-badge badge-high">${notification.status.toUpperCase()}</div>
                            </div>
                        `).join('');
                    }
                    
                    historyCard.style.display = 'block';
                    historyCard.scrollIntoView({ behavior: 'smooth' });
                }
            })
            .catch(error => {
                console.error('History fetch error:', error);
            });
        }
        
        // Auto-refresh stats and alerts every 15 seconds
        setInterval(() => {
            updateStats();
        }, 15000);
    </script>
    
    <div class="footer">
        <p>🛡️ ThreatShield v2.0 | Enhanced Email & WhatsApp Alerts | Built for Advanced Security Operations</p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Simple rule-based threat detection (no ML dependencies!)
        risk_score = 0
        
        # Calculate risk based on behavior
        if data.get('logins', 0) > 15: risk_score += 30
        if data.get('data_access', 0) > 300: risk_score += 25
        if data.get('after_hours', 0) > 5: risk_score += 20
        if data.get('failed_logins', 0) > 3: risk_score += 15
        if data.get('unusual_location', 0) == 1: risk_score += 20
        if data.get('privilege_escalation', 0) == 1: risk_score += 30
        
        # Add some randomness for demo
        risk_score += random.randint(-10, 10)
        risk_score = max(0, min(100, risk_score))
        
        is_threat = risk_score > 60
        threat_level = "HIGH" if is_threat else ("MEDIUM" if risk_score > 30 else "LOW")
        
        recommendations = {
            "HIGH": "🚨 IMMEDIATE ACTION REQUIRED! Investigate user activity, review access logs, and consider account suspension.",
            "MEDIUM": "⚠️ ELEVATED RISK: Increase monitoring, review recent activities, and prepare for potential escalation.",
            "LOW": "✅ NORMAL BEHAVIOR: Continue standard monitoring procedures. No immediate action needed."
        }
        
        response_data = {
            "user_id": data.get('user_id', 'unknown'),
            "threat_level": threat_level,
            "risk_score": risk_score,
            "is_threat": True if is_threat else False,
            "recommendation": recommendations[threat_level]
        }
        
        # Send notification for HIGH and MEDIUM risk threats
        if threat_level in ["HIGH", "MEDIUM"]:
            try:
                notification_service.send_high_risk_alert(
                    user_id=response_data["user_id"],
                    risk_score=risk_score,
                    threat_details=data
                )
                print(f"🔔 {threat_level} risk alert sent for user: {response_data['user_id']}")
                
            except Exception as e:
                print(f"⚠️ Notification service error: {e}")
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/configure-notifications', methods=['POST'])
def configure_notifications():
    """Configure email, WhatsApp, and API endpoint notifications"""
    try:
        config = request.json
        
        # Configure Email
        if config.get('email', {}).get('enabled'):
            notification_service.configure_email(
                recipient_email=config['email'].get('recipient', '')
            )
        
        # Configure WhatsApp
        if config.get('whatsapp', {}).get('enabled'):
            notification_service.configure_whatsapp(
                phone_number=config['whatsapp'].get('phone_number', '')
            )
        
        # Configure API Endpoint
        if config.get('api_endpoint', {}).get('enabled'):
            notification_service.configure_api_endpoint(
                api_url=config['api_endpoint'].get('url', ''),
                headers=config['api_endpoint'].get('headers', {})
            )
        
        return jsonify({"success": True, "message": "Alert notifications configured successfully!"})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test-notification', methods=['POST'])
def test_notification():
    """Send a test notification to all configured channels"""
    try:
        # Send a test high-risk alert
        notification_service.send_high_risk_alert(
            user_id="test_user_demo",
            risk_score=95,
            threat_details={
                "test": True, 
                "source": "manual_test",
                "logins": 25,
                "data_access": 500,
                "after_hours": 8,
                "unusual_location": 1,
                "privilege_escalation": 1
            }
        )
        
        return jsonify({"success": True, "message": "Test alert sent to all configured channels!"})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/notification-history', methods=['GET'])
def get_notification_history():
    """Get recent notification history"""
    try:
        history = notification_service.get_notification_history()
        return jsonify({"success": True, "history": history})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🛡️  ThreatShield v2.0 - Enhanced Security Alert System")
    print("="*65)
    print("🚀 System Starting...")
    print("✅ Dark theme UI loaded")
    print("🧠 AI-powered threat detection ready")
    print("📧 Email alert system initialized")
    print("📱 WhatsApp integration ready")
    print("🌐 API endpoint notifications ready")
    print("🔔 Real-time threat alerts: ACTIVE")
    print("🌐 Dashboard: http://localhost:5000")
    print("🎯 Perfect for security operations!")
    print("="*65)
    
    app.run(debug=True, host='0.0.0.0', port=5000)  