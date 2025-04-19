from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter

router = APIRouter()


api_exceptions_total = Counter(
    "api_exceptions_total", "Total number of uncaught exceptions in the API"
)


@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
