from flask import Flask, request, jsonify
import os
import firebase_admin
from firebase_admin import credentials, messaging
import base64
import json
import random

app = Flask(__name__)

# Initialize Firebase
def initialize_firebase():
    try:
        # Get Firebase credentials from environment variable (base64 encoded)
        cred_json = base64.b64decode(os.environ["FIREBASE_CRED_JSON"]).decode()
        cred = credentials.Certificate(json.loads(cred_json))
        firebase_admin.initialize_app(cred)
        return True
    except Exception as e:
        print(f"Firebase initialization failed: {str(e)}")
        return False

# Initialize Firebase when app starts
if not initialize_firebase():
    raise RuntimeError("Failed to initialize Firebase")

# Message templates
CUTE_MESSAGES = [
    "Just thinking about you makes me smile. 😊",
    "You’re the best thing that ever happened to me. 💖",
    "I don’t need a reason to miss you—I just do. All the time.",
    "You’re my favorite notification. 📱❤️",
    "If I had to choose between you and chocolate, I’d choose you… after eating the chocolate. 😘",
    "You’re like a cozy blanket for my soul.",
    "I love the way you make ordinary moments feel magical.",
    "You’re my favorite daydream.",
    "Life is so much better with you in it.",
    "I’d rather have a bad day with you than a good day with anyone else.",
    "You’re my happy place. 🌸",
    "I don’t just miss you—I miss the way you make me feel.",
    "You’re the reason I believe in love.",
    "I could never get tired of loving you.",
    "My heart does a little dance every time I see your name pop up on my phone. 💃",
    "You’re the human version of sunshine. ☀️",
    "I love you more than yesterday, but less than tomorrow.",
    "You make my heart skip a beat—and not just because you scare me sometimes. 😆",
    "I don’t need a thousand wishes—I already have you.",
    "You’re my favorite adventure.",
    "Being with you feels like coming home.",
    "I love you more than pizza… and that’s saying a lot. 🍕",
    "You’re the missing piece to my puzzle.",
    "Every love song reminds me of you.",
    "I fall for you more every single day.",
    "You’re my favorite kind of chaos.",
    "I love the way you understand me without me having to say a word.",
    "You’re my favorite person to do nothing with.",
    "I don’t just love you—I really, really like you.",
    "You’re the reason I believe in soulmates.",
    "I could get lost in your eyes forever.",
    "You’re my favorite thought.",
    "Loving you is the easiest thing I’ve ever done.",
    "You make my heart feel full.",
    "I love the way you laugh at my terrible jokes.",
    "You’re my favorite distraction.",
    "I don’t need a genie—I already have everything I want in you.",
    "You’re my favorite kind of beautiful.",
    "I love the way you make even the simplest moments special.",
    "You’re my favorite reason to smile.",
    "I love you more than coffee… and that’s serious. ☕",
    "You’re my favorite sound, my favorite sight, my favorite everything.",
    "I’d choose you over sleep… and I *really* love sleep. 😴❤️",
    "You make my heart feel like it’s on a trampoline—bouncy and happy.",
    "I love the way you fit perfectly into my arms.",
    "You’re my favorite kind of trouble.",
    "I love you more than words can say… but I’ll keep trying anyway.",
    "You’re my favorite kind of magic.",
    "I love the way you make my heart race just by being you.",
    "No matter what happens, I’ll always choose you—again and again."
]

RANDOM_TITLES = [
    "💌 A Special Message For You!",
    "✨ You're Magical!",
    "🥰 My Heart Skips a Beat",
    "🌹 Thinking of You",
    "💖 Love Alert!",
    "🌟 You Shine Bright",
    "🤗 Virtual Hug Incoming",
    "😘 Sending You Kisses",
    "💕 You're My Favorite",
    "🌈 My Personal Sunshine"
]


def send_fcm_message(fcm_token=None, custom_message=None, custom_title=None):
    """Send an FCM message with custom or random content"""
    try:
        # Use provided token or default from environment
        token = fcm_token if fcm_token else os.environ.get("DEFAULT_FCM_TOKEN")
        
        if not token:
            return {
                "success": False,
                "message": "No FCM token provided"
            }

        # Use custom or random message/title
        title = custom_title if custom_title else random.choice(RANDOM_TITLES)
        message_body = custom_message if custom_message else random.choice(CUTE_MESSAGES)

        # Send FCM
        response = messaging.send(messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message_body
            ),
            token=token
        ))
        
        return {
            "success": True,
            "message": "Message sent successfully",
            "title": title,
            "body": message_body,
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
    """API endpoint to send a message"""
    data = request.get_json() or {}
    
    result = send_fcm_message(
        fcm_token=data.get('fcm_token'),
        custom_message=data.get('message'),
        custom_title=data.get('title')
    )
    
    status_code = 200 if result["success"] else 400
    return jsonify(result), status_code

@app.route('/send-random', methods=['GET'])
def send_random_message():
    """Send a random message to default device"""
    result = send_fcm_message()
    status_code = 200 if result["success"] else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
