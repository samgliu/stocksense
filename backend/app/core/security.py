from fastapi import Header, HTTPException, Depends
from app.services.firebase import firebase_admin
from firebase_admin import auth as firebase_auth


async def verify_firebase_token(token: str):
    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
