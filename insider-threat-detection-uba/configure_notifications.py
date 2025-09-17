#!/usr/bin/env python3
"""
Configure ThreatShield Mobile Notifications
Run this to set up your Android app, WhatsApp, and Email notifications
"""

import requests
import json

def configure_notifications():
    """Configure all notification channels"""
    
    print("🛡️ ThreatShield Mobile Notifications Setup")
    print("=" * 50)
    
    # Configuration for all three channels
    config = {
        "android_app": {
            "enabled": True,
            "api_endpoint": "http://your-android-app-server.com/api/notifications",  # Replace with your app's endpoint
            "api_key": ""  # Optional: Add your API key if needed
        },
        "whatsapp": {
            "enabled": True,
            "phone_number": "+1234567890",  # Replace with your phone number
            "api_key": ""  # For Twilio or WhatsApp Business API
        },
        "email": {
            "enabled": True,
            "recipient_email": "your-email@gmail.com",  # Replace with your email
            "sender_email": "threatshield@gmail.com",   # Replace with sender email
            "sender_password": "your-app-password"      # Use App Password for Gmail
        }
    }
    
    try:
        # Send configuration to notification service
        response = requests.post('http://localhost:5001/api/configure', json=config)
        result = response.json()
        
        if result['success']:
            print("✅ Notifications configured successfully!")
            print("\n📱 Configured channels:")
            print(f"   - Android App: {config['android_app']['api_endpoint']}")
            print(f"   - WhatsApp: {config['whatsapp']['phone_number']}")
            print(f"   - Email: {config['email']['recipient_email']}")
        else:
            print(f"❌ Configuration failed: {result['error']}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Notification service not running!")
        print("   Please start it first: python mobile_notifications.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_notifications():
    """Send test notifications"""
    
    print("\n🧪 Testing Notifications...")
    
    try:
        response = requests.post('http://localhost:5001/api/test')
        result = response.json()
        
        if result['success']:
            print("✅ Test notifications sent!")
            print("   Check your Android app, WhatsApp, and email")
        else:
            print(f"❌ Test failed: {result['error']}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Notification service not running!")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_integration_example():
    """Show how your Android app should receive notifications"""
    
    print("\n📱 Android App Integration Example:")
    print("-" * 40)
    print("""
Your Android app will receive POST requests like this:

POST http://your-app-server.com/api/notifications
Content-Type: application/json

{
    "title": "ThreatShield Alert - HIGH Risk",
    "message": "🚨 THREAT DETECTED!\\n\\nUser: user_123\\nThreat Level: HIGH\\nRisk Score: 85%\\nTime: 14:30:15\\nAction: Immediate Investigation",
    "data": {
        "alert_type": "insider_threat",
        "threat_level": "HIGH",
        "user_id": "user_123",
        "risk_score": 85,
        "timestamp": "2024-09-17T14:30:15.123456"
    }
}

In your Android app (Kotlin/Java):
1. Set up a webhook endpoint to receive these POST requests
2. Parse the JSON payload
3. Show notification to user
4. Optional: Store in local database
    """)

if __name__ == '__main__':
    print("Choose an option:")
    print("1. Configure notifications")
    print("2. Test notifications")
    print("3. Show Android integration example")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        configure_notifications()
    elif choice == '2':
        test_notifications()
    elif choice == '3':
        show_integration_example()
    else:
        print("Invalid choice!")