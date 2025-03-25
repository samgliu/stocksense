import os
import firebase_admin
from firebase_admin import credentials

key_path = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS", "credentials/serviceAccountKey.json"
)

cred = credentials.Certificate(key_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
