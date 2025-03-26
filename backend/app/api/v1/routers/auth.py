from fastapi import APIRouter, Request
from app.core.decorators import verify_token  # make sure this exists

router = APIRouter()


@router.get("/auth")
@verify_token
async def protected_route(request: Request):
    user = request.state.user
    return {
        "email": user.get("email"),
        "uid": user.get("uid"),
        "name": user.get("name"),
    }
