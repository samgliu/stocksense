from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from app.core.security import verify_firebase_token


class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = ["/health", "/docs", "/openapi.json"]
        if request.url.path in public_paths:
            return await call_next(request)
        if request.url.path == "/metrics":
            auth_header = request.headers.get("X-Internal-Api-Key")
            try:
                INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")
                if auth_header and auth_header == INTERNAL_API_KEY:
                    return await call_next(request)
            except Exception:
                pass
            raise HTTPException(
                status_code=401,
                detail="Unauthorized for /metrics",
                headers={"WWW-Authenticate": "Basic"},
            )
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                user = await verify_firebase_token(token)
                request.state.user = user
            except Exception:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
        else:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return await call_next(request)


def add_firebase_auth_middleware(app):
    app.add_middleware(FirebaseAuthMiddleware)
