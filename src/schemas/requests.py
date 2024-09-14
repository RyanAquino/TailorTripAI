from datetime import datetime
from pydantic import BaseModel, Field


class GenerateScheduleQueryParams(BaseModel):
    tags: list[str] = Field(..., description="List of tags")
    from_date: datetime = Field(..., description="Start date")
    to_date: datetime = Field(..., description="End date")
    travel_location: str = Field(..., description="Travel location")
    home_location: str = Field(..., description="Home location")
