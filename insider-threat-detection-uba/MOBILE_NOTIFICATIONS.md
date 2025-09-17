# 📱 ThreatShield Mobile Notifications

## Overview
Simple 3-channel notification system for HIGH and MEDIUM threat alerts:
1. **Android App** - Direct API integration
2. **WhatsApp** - Via phone number  
3. **Email** - SMTP notifications

## Quick Setup

### 1. Start the Notification Service
```bash
python mobile_notifications.py
```
*Runs on http://localhost:5001*

### 2. Start ThreatShield Dashboard  
```bash
python simple_app.py
```
*Runs on http://localhost:5000*

### 3. Configure Notifications
```bash
python configure_notifications.py
```

## 🚀 For Your Android App

### API Endpoint Format
Your Android app needs to handle POST requests at your endpoint:

```json
POST http://your-android-app-server.com/api/notifications
{
    "title": "ThreatShield Alert - HIGH Risk",
    "message": "🚨 THREAT DETECTED!\n\nUser: user_123\nThreat Level: HIGH\nRisk Score: 85%",
    "data": {
        "alert_type": "insider_threat",
        "threat_level": "HIGH", 
        "user_id": "user_123",
        "risk_score": 85,
        "timestamp": "2024-09-17T14:30:15.123456"
    }
}
```

### Android Integration Steps
1. **Set up webhook endpoint** in your Android backend
2. **Parse JSON payload** when notification arrives  
3. **Show push notification** to user
4. **Optional:** Store alert in local database

## 📞 WhatsApp Setup (Optional)

For real WhatsApp integration, use Twilio:

1. Sign up at [Twilio](https://twilio.com)
2. Get WhatsApp Business API access
3. Add your Twilio credentials in `mobile_notifications.py`
4. Update phone number format: `+1234567890`

## 📧 Email Setup (Optional)

For Gmail SMTP:

1. Enable 2-factor authentication on Gmail
2. Generate App Password: Google Account → Security → App Passwords
3. Use app password instead of regular password
4. Update email config in `configure_notifications.py`

## 🧪 Testing

### Send Test Alert
```bash
curl -X POST http://localhost:5001/api/test
```

### Manual Alert (from your code)
```python
import requests

payload = {
    "user_id": "demo_user", 
    "threat_level": "HIGH",
    "risk_score": 85,
    "details": {"source": "manual_test"}
}

response = requests.post('http://localhost:5001/api/send-alert', json=payload)
```

## 🎯 Demo Flow for Hackathon

1. **Configure** your Android app endpoint
2. **Generate high-risk user** in ThreatShield (logins=25, data_access=600)
3. **Click "Analyze Threat"** 
4. **Watch notification** sent to your Android app automatically!
5. **Show notification history** in ThreatShield dashboard

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Service status |
| `/api/configure` | POST | Configure notification channels |
| `/api/send-alert` | POST | Send threat alert |
| `/api/test` | POST | Send test notifications |
| `/api/history` | GET | Get notification history |

## 🔧 Customization

Edit `mobile_notifications.py` to:
- Change notification message format
- Add more notification channels
- Modify threat level filtering
- Add authentication/security

Perfect for hackathon demos! 🏆