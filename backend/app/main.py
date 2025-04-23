import logging

import app.services.firebase
from app.api.v1.routers import (
    auth,
    auto_trade,
    companies,
    dashboard,
    health,
    job_stream,
    metrics,
    search,
    stock,
    worker,
)
from app.cron.cron import start_autotrade_scheduler
from app.middleware.cors import add_cors_middleware
from app.middleware.firebase import add_firebase_auth_middleware
from app.middleware.gzip import add_gzip_middleware
from app.middleware.ratelimit import add_rate_limit_middleware
from app.middleware.security import add_security_headers
from app.services.sentry import setup_sentry
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

app = FastAPI()
setup_sentry(app)


# Scheduler
@app.on_event("startup")
async def startup_event():
    start_autotrade_scheduler()


# Middleware
add_firebase_auth_middleware(app)
add_cors_middleware(app)
add_security_headers(app)
add_gzip_middleware(app)
add_rate_limit_middleware(app)

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(stock.router, prefix="/api/v1/stock", tags=["Stock"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["Companies"])
app.include_router(worker.router, prefix="/api/v1/worker", tags=["Worker"])
app.include_router(auto_trade.router, prefix="/api/v1/auto-trade", tags=["Auto Trade"])
app.include_router(metrics.router)

# Websockets
app.include_router(job_stream.router, prefix="/api/v1", tags=["Job Stream"])
