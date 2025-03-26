from fastapi import Request, HTTPException, status
from functools import wraps
from app.core.security import verify_firebase_token


def verify_token(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request") or next(
            (a for a in args if isinstance(a, Request)), None
        )
        if not request:
            raise HTTPException(status_code=500, detail="Request object missing")

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")

        try:
            token = auth_header.split(" ")[1]
            user = await verify_firebase_token(token)
            request.state.user = user
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

        return await func(*args, **kwargs)

    return wrapper
