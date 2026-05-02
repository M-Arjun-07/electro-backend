import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import json

# For deployment (e.g., Render), use environment variable for service account JSON
# For local dev, fallback to serviceAccountKey.json
CERT_PATH = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
FIREBASE_JSON = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")

if not firebase_admin._apps:
    if FIREBASE_JSON:
        try:
            # Parse the JSON string from environment variable
            service_account_info = json.loads(FIREBASE_JSON)
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized using environment variable.")
        except Exception as e:
            print(f"Failed to initialize Firebase from env var: {e}")
    elif os.path.exists(CERT_PATH):
        cred = credentials.Certificate(CERT_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized using local serviceAccountKey.json.")
    else:
        print("\n" + "="*60)
        print("ERROR: Firebase Service Account Key Missing!")
        print("Please set FIREBASE_SERVICE_ACCOUNT_JSON env var or place 'serviceAccountKey.json' in backend folder.")
        print("="*60 + "\n")
        try:
            firebase_admin.initialize_app()
        except Exception:
            pass

try:
    db = firestore.client()
except Exception as e:
    print(f"Firestore client initialization failed: {e}")
    db = None

def verify_token(token):
    if not token: return None
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None
