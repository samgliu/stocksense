from fastapi import Request, HTTPException
from functools import wraps


def require_admin(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request") or ...
        user = getattr(request.state, "user", {})
        if user.get("role") != "Admin":
            raise HTTPException(status_code=403, detail="Admins only")
        return await func(*args, **kwargs)

    return wrapper
