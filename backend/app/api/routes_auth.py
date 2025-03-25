# app/api/routes_auth.py
from fastapi import APIRouter, Depends
from app.deps.auth import verify_token

router = APIRouter()


@router.get("/protected")
def protected_route(user=Depends(verify_token)):
    return {"email": user["email"], "uid": user["uid"], "fullname": user["name"]}
