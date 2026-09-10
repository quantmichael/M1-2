from datetime import datetime

from pydantic import BaseModel


class DataCreate(BaseModel):
    date: datetime
    value: float
    memo: str = ""
    peak_to_peak: float | None = None
    sample_count: int | None = None


class DataUpdate(BaseModel):
    date: datetime | None = None
    value: float | None = None
    memo: str | None = None
    peak_to_peak: float | None = None
    sample_count: int | None = None