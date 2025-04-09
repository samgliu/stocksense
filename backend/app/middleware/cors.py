from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os

def add_cors_middleware(app: FastAPI):
    allow_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://192.168.7.180:3000").split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
