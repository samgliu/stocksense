from fastapi import Header, HTTPException, Depends
from app.services.firebase import firebase_admin
from firebase_admin import auth as firebase_auth

async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]
    try:
        decoded = firebase_auth.verify_id_token(token)
        print(f"Decoded token: {decoded}")
        return decoded  # contains uid, email, etc.
    except Exception as e:
        print(f"exception: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
