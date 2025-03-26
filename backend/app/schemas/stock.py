from pydantic import BaseModel


class StockRequest(BaseModel):
    text: str


class StockResponse(BaseModel):
    summary: str
