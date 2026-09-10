import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

SERVICE_ACCOUNT_PATH = (
    BASE_DIR
    / "secrets"
    / "firebase-service-account.json"
)


if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)


db = firestore.client()