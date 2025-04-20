import os

import sentry_sdk
from app.api.v1.routers.metrics import api_exceptions_total
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


def setup_sentry(app: FastAPI):
    """
    Initialize Sentry and register global exception handlers for the FastAPI app.
    """
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        traces_sample_rate=0,
        sample_rate=0.1,
        environment=os.getenv("ENV", "production"),
        send_default_pii=True,
    )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        sentry_sdk.capture_exception(exc)
        api_exceptions_total.inc()
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        if exc.status_code >= 500:
            sentry_sdk.capture_exception(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
