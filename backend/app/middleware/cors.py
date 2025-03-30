from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


def add_cors_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://192.168.7.180:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
