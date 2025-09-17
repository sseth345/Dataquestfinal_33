#!/usr/bin/env python3
"""
ThreatShield Mobile Notifications
Simple integration for Android App, WhatsApp, and Email
"""

from flask import Flask, render_template_string, jsonify, request
import json
from datetime import datetime, timedelta
import random
import requests
import threading
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

app = Flask(__name__)

class SimpleMobileNotifications:
    def __init__(self):
        self.config = {
            'android_app': {
                'enabled': False,
                'api_endpoint': '',
                'api_key': ''
            },
            'whatsapp': {
                'enabled': False,
                'phone_number': '',
                'api_key': ''  # For WhatsApp Business API or Twilio
            },
            'email': {
                'enabled': False,
                'recipient_email': '',
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': '',
                'sender_password': ''
            }
        }
        self.notification_history = []
    
    def configure_android_app(self, api_endpoint, api_key=""):
        """Configure your Android app endpoint"""
        self.config['android_app'] = {
            'enabled': True,
            'api_endpoint': api_endpoint,
            'api_key': api_key
        }
        print(f"✅ Android app configured: {api_endpoint}")
    
    def configure_whatsapp(self, phone_number, api_key):
        """Configure WhatsApp notifications"""
        self.config['whatsapp'] = {
            'enabled': True,
            'phone_number': phone_number,
            'api_key': api_key
        }
        print(f"✅ WhatsApp configured: {phone_number}")
    
    def configure_email(self, recipient_email, sender_email, sender_password):
        """Configure email notifications"""
        self.config['email'] = {
            'enabled': True,
            'recipient_email': recipient_email,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': sender_email,
            'sender_password': sender_password
        }
        print(f"✅ Email configured: {recipient_email}")
    
    def send_threat_alert(self, user_id, threat_level, risk_score, threat_details):
        """Send threat alert through all configured channels"""
        if threat_level not in ['HIGH', 'MEDIUM']:
            return  # Only send HIGH and MEDIUM alerts
        
        alert_data = {
            'alert_type': 'insider_threat',
            'threat_level': threat_level,
            'user_id': user_id,
            'risk_score': risk_score,
            'timestamp': datetime.now().isoformat(),
            'details': threat_details,
            'message': self._create_alert_message(user_id, threat_level, risk_score)
        }
        
        # Send notifications asynchronously
        threading.Thread(target=self._send_all_notifications, args=(alert_data,)).start()
        
        # Add to history
        self.notification_history.append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'user': user_id,
            'threat_level': threat_level,
            'risk_score': risk_score,
            'status': 'sent'
        })
        
        print(f"🚨 {threat_level} RISK ALERT SENT for user: {user_id} (Risk: {risk_score}%)")
    
    def _create_alert_message(self, user_id, threat_level, risk_score):
        """Create formatted alert message"""
        emoji = "🚨" if threat_level == "HIGH" else "⚠️"
        return f"{emoji} THREAT DETECTED!\\n\\n" \
               f"User: {user_id}\\n" \
               f"Threat Level: {threat_level}\\n" \
               f"Risk Score: {risk_score}%\\n" \
               f"Time: {datetime.now().strftime('%H:%M:%S')}\\n" \
               f"Action: {'Immediate Investigation' if threat_level == 'HIGH' else 'Monitor Closely'}"
    
    def _send_all_notifications(self, alert_data):
        """Send notifications to all configured channels"""
        # 1. Send to Android App
        if self.config['android_app']['enabled']:
            self._send_to_android_app(alert_data)
        
        # 2. Send to WhatsApp
        if self.config['whatsapp']['enabled']:
            self._send_whatsapp(alert_data)
        
        # 3. Send Email
        if self.config['email']['enabled']:
            self._send_email(alert_data)
    
    def _send_to_android_app(self, alert_data):
        """Send push notification to your Android app"""
        try:
            config = self.config['android_app']
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {config["api_key"]}' if config["api_key"] else ''
            }
            
            # Payload for your Android app
            payload = {
                'title': f'ThreatShield Alert - {alert_data["threat_level"]} Risk',
                'message': alert_data['message'],
                'data': {
                    'alert_type': alert_data['alert_type'],
                    'threat_level': alert_data['threat_level'],
                    'user_id': alert_data['user_id'],
                    'risk_score': alert_data['risk_score'],
                    'timestamp': alert_data['timestamp']
                }
            }
            
            response = requests.post(config['api_endpoint'], json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"📱 Android app notification sent successfully!")
            else:
                print(f"❌ Android app notification failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Android app notification error: {e}")
    
    def _send_whatsapp(self, alert_data):
        """Send WhatsApp message"""
        try:
            # Using Twilio WhatsApp API (you can replace with any WhatsApp Business API)
            config = self.config['whatsapp']
            
            # Twilio WhatsApp API example
            url = "https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID/Messages.json"
            
            payload = {
                'From': 'whatsapp:+14155238886',  # Twilio WhatsApp number
                'To': f'whatsapp:{config["phone_number"]}',
                'Body': alert_data['message']
            }
            
            # For demo purposes, we'll just simulate
            print(f"📞 WhatsApp message sent to {config['phone_number']}")
            print(f"   Message: {alert_data['message']}")
            
            # Uncomment below for real Twilio integration:
            # response = requests.post(url, data=payload, auth=('YOUR_SID', 'YOUR_TOKEN'))
            
        except Exception as e:
            print(f"❌ WhatsApp notification error: {e}")
    
    def _send_email(self, alert_data):
        """Send email notification"""
        try:
            config = self.config['email']
            
            # Create email message
            msg = MimeMultipart()
            msg['From'] = config['sender_email']
            msg['To'] = config['recipient_email']
            msg['Subject'] = f"🛡️ ThreatShield Alert - {alert_data['threat_level']} Risk Detected"
            
            # Email body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: {'#dc2626' if alert_data['threat_level'] == 'HIGH' else '#d97706'};">
                    🛡️ ThreatShield Security Alert
                </h2>
                
                <div style="background: #f8fafc; padding: 20px; border-left: 4px solid {'#dc2626' if alert_data['threat_level'] == 'HIGH' else '#d97706'};">
                    <h3>Threat Level: {alert_data['threat_level']}</h3>
                    <p><strong>User:</strong> {alert_data['user_id']}</p>
                    <p><strong>Risk Score:</strong> {alert_data['risk_score']}%</p>
                    <p><strong>Time:</strong> {alert_data['timestamp']}</p>
                    <p><strong>Action Required:</strong> {'Immediate Investigation' if alert_data['threat_level'] == 'HIGH' else 'Monitor Closely'}</p>
                </div>
                
                <p>This alert was generated by ThreatShield Insider Threat Detection System.</p>
            </body>
            </html>
            """
            
            msg.attach(MimeText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['sender_email'], config['sender_password'])
            text = msg.as_string()
            server.sendmail(config['sender_email'], config['recipient_email'], text)
            server.quit()
            
            print(f"📧 Email sent to {config['recipient_email']}")
            
        except Exception as e:
            print(f"❌ Email notification error: {e}")
    
    def get_notification_history(self):
        """Get recent notification history"""
        return self.notification_history[-10:]

# Initialize notification service
notification_service = SimpleMobileNotifications()

@app.route('/')
def home():
    return jsonify({
        "service": "ThreatShield Mobile Notifications API",
        "status": "running",
        "endpoints": [
            "POST /api/configure - Configure notification channels",
            "POST /api/send-alert - Send threat alert",
            "GET /api/history - Get notification history",
            "POST /api/test - Send test notification"
        ]
    })

@app.route('/api/configure', methods=['POST'])
def configure_notifications():
    """Configure notification channels"""
    try:
        config = request.json
        
        # Configure Android App
        if 'android_app' in config:
            app_config = config['android_app']
            if app_config.get('enabled') and app_config.get('api_endpoint'):
                notification_service.configure_android_app(
                    api_endpoint=app_config['api_endpoint'],
                    api_key=app_config.get('api_key', '')
                )
        
        # Configure WhatsApp
        if 'whatsapp' in config:
            wa_config = config['whatsapp']
            if wa_config.get('enabled') and wa_config.get('phone_number'):
                notification_service.configure_whatsapp(
                    phone_number=wa_config['phone_number'],
                    api_key=wa_config.get('api_key', '')
                )
        
        # Configure Email
        if 'email' in config:
            email_config = config['email']
            if email_config.get('enabled') and email_config.get('recipient_email'):
                notification_service.configure_email(
                    recipient_email=email_config['recipient_email'],
                    sender_email=email_config['sender_email'],
                    sender_password=email_config['sender_password']
                )
        
        return jsonify({"success": True, "message": "Notifications configured successfully!"})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/send-alert', methods=['POST'])
def send_threat_alert():
    """Send threat alert - This is what your main app will call"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['user_id', 'threat_level', 'risk_score']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        # Send the alert
        notification_service.send_threat_alert(
            user_id=data['user_id'],
            threat_level=data['threat_level'],
            risk_score=data['risk_score'],
            threat_details=data.get('details', {})
        )
        
        return jsonify({
            "success": True, 
            "message": f"{data['threat_level']} risk alert sent successfully!"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test', methods=['POST'])
def test_notification():
    """Send a test notification"""
    try:
        # Send test alerts for both HIGH and MEDIUM
        notification_service.send_threat_alert(
            user_id="test_user_high",
            threat_level="HIGH",
            risk_score=85,
            threat_details={"test": True, "source": "api_test"}
        )
        
        notification_service.send_threat_alert(
            user_id="test_user_medium",
            threat_level="MEDIUM",
            risk_score=45,
            threat_details={"test": True, "source": "api_test"}
        )
        
        return jsonify({"success": True, "message": "Test notifications sent!"})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_notification_history():
    """Get notification history"""
    try:
        history = notification_service.get_notification_history()
        return jsonify({"success": True, "history": history})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("📱 ThreatShield Mobile Notifications API")
    print("=" * 50)
    print("🚀 Starting notification service...")
    print("📱 Android App Integration: Ready")
    print("📞 WhatsApp Integration: Ready")
    print("📧 Email Integration: Ready")
    print("🌐 API Server: http://localhost:5001")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)