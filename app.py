from flask import Flask, request, jsonify
import os
import firebase_admin
from firebase_admin import credentials, messaging, firestore
import base64
import json
import datetime

app = Flask(__name__)

# Initialize Firebase
def initialize_firebase():
    try:
        # Get Firebase credentials from environment variable (base64 encoded)
        cred_json = base64.b64decode(os.environ["FIREBASE_CRED_JSON"]).decode()
        cred = credentials.Certificate(json.loads(cred_json))
        firebase_admin.initialize_app(cred)
        # Initialize Firestore
        global db
        db = firestore.client()
        return True
    except Exception as e:
        print(f"Firebase initialization failed: {str(e)}")
        return False

# Initialize Firebase when app starts
if not initialize_firebase():
    raise RuntimeError("Failed to initialize Firebase")

def store_message(message_text, time_window):
    """Log the message in Firestore."""
    try:
        doc_ref = db.collection("love_messages").document()
        doc_ref.set({
            "message": message_text,
            "time_window": time_window,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "date": datetime.date.today().isoformat()
        })
        return True
    except Exception as e:
        print(f"Firestore error: {e}")
        return False

def send_fcm_message(fcm_token=None, custom_message=None, custom_title=None, time_window=None):
    """Send an FCM message with custom content and store in Firestore"""
    try:
        # Use provided token or default from environment
        token = fcm_token if fcm_token else os.environ.get("DEFAULT_FCM_TOKEN")
        
        if not token:
            return {
                "success": False,
                "message": "No FCM token provided"
            }

        if not custom_message or not custom_title:
            return {
                "success": False,
                "message": "Message and title are required"
            }

        # Store message in Firestore
        store_success = store_message(custom_message, time_window)
        if not store_success:
            return {
                "success": False,
                "message": "Failed to store message in Firestore"
            }

        # Send FCM with high priority
        message = messaging.Message(
            notification=messaging.Notification(
                title=custom_title,
                body=custom_message
            ),
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    priority='high'
                )
            ),
            apns=messaging.APNSConfig(
                headers={
                    'apns-priority': '10',
                },
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        content_available=True,
                        # Remove the priority parameter from Aps
                    )
                )
            ),
            token=token
        )
        
        response = messaging.send(message)
        
        return {
            "success": True,
            "message": "Message sent and stored successfully",
            "title": custom_title,
            "body": custom_message,
            "response": response
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error sending message: {str(e)}"
        }

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/send-message', methods=['POST'])
def send_message_api():
    """API endpoint to send a message and store it in Firestore"""
    data = request.get_json() or {}
    
    result = send_fcm_message(
        fcm_token=data.get('fcm_token'),
        custom_message=data.get('message'),
        custom_title=data.get('title'),
        time_window=data.get('time_window')
    )
    
    status_code = 200 if result["success"] else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
