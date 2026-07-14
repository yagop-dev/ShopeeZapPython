from pydantic import BaseModel
from typing import Optional

class PromotionRequest(BaseModel):
    original_url: str
    description: str
    price: str

class PromotionResponse(BaseModel):
    success: bool
    message: str
    converted_url: Optional[str] = None