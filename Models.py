from pydantic import BaseModel, Field
from datetime import datetime


class CoilCreate(BaseModel):
    length: int = Field(..., gt=0)
    weight: int = Field(..., gt=0)


class CoilInDB(BaseModel):
    id: int
    length: int
    weight: int
    created_at: datetime
    deleted_at: datetime | None


class CoilStats(BaseModel):
    added_count: int
    deleted_count: int
    avg_length: float
    avg_weight: float
    min_length: int
    max_length: int
    min_weight: int
    max_weight: int
    total_weight: int
    min_storage_time: datetime
    max_storage_time: datetime
