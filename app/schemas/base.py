from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool
    message: str
    
    class Config:
        from_attributes = True


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
