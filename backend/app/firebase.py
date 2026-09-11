import json
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore


BASE_DIR = Path(__file__).resolve().parents[2]


def initialize_firebase():

    if firebase_admin._apps:
        return

    service_account_json = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_JSON"
    )

    if service_account_json:

        service_account_info = json.loads(
            service_account_json
        )

        cred = credentials.Certificate(
            service_account_info
        )

    else:

        service_account_path = (
            BASE_DIR
            / "secrets"
            / "firebase-service-account.json"
        )

        if not service_account_path.exists():
            raise FileNotFoundError(
                "Firebase 서비스 계정 정보를 찾을 수 없습니다."
            )

        cred = credentials.Certificate(
            service_account_path
        )

    firebase_admin.initialize_app(
        cred
    )


initialize_firebase()

db = firestore.client()