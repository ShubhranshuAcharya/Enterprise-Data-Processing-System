from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class Record(BaseModel):
    id: int
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    amount: float = Field(..., gt=0)
    status: str
    created_at: datetime
    
    @validator('status')
    @classmethod
    def validate_status(cls, v):
        if v.lower() not in ['pending', 'completed', 'failed']:
            raise ValueError("Status must be 'pending', 'completed', or 'failed'")
        return v.lower()
