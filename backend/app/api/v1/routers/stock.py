from fastapi import APIRouter, Request, Depends, UploadFile, File, Form
from app.schemas.stock import StockRequest, StockResponse
from app.services.stock_analysis import analyze_stock
from app.core.decorators import verify_token

router = APIRouter()


@router.post("/analyze", response_model=StockResponse)
@verify_token
async def analyze_stock_endpoint(request: Request, body: StockRequest):
    result = analyze_stock(body.text)
    return {"summary": result}
