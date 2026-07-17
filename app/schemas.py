from pydantic import BaseModel
from typing import Optional, Dict, Any

class PromotionRequest(BaseModel):
    original_url: str
    description: str
    price: str

class PromotionResponse(BaseModel):
    success: bool
    message: str
    converted_url: Optional[str] = None

class WebHookData(BaseModel):
    event: str
    instance: str
    data: Dict[str, Any]