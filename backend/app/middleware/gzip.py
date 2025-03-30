from fastapi.middleware.gzip import GZipMiddleware
from fastapi import FastAPI


def add_gzip_middleware(app: FastAPI):
    app.add_middleware(GZipMiddleware, minimum_size=1000)
