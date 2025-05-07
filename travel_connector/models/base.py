"""
Base model class that all other standardized models will inherit from.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel as PydanticBaseModel, Field, validator

class BaseModel(PydanticBaseModel):
    """Base class for all standardized data models"""
    
    id: str = Field(..., description="Unique identifier for the entity")
    source: str = Field(..., description="Source API or system identifier")
    source_id: str = Field(..., description="Original ID from the source system")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Original raw data from source")

    @validator('updated_at', always=True)
    def set_updated_at(cls, v):
        """Always set updated_at to current time on model update"""
        return datetime.utcnow()
    
    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
