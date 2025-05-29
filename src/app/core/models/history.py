from pydantic import BaseModel, Field


class HistoryResponse(BaseModel):
    """
    History response model
    """

    id: int = Field(description="History record ID")
    session_id: str = Field(description="Session ID")
    city: str = Field(description="City name")
    country: str = Field(description="Country name")
    latitude: float = Field(description="Latitude")
    longitude: float = Field(description="Longitude")


class HistoryListResponse(BaseModel):
    """
    History list response model
    """

    status: str = Field(default="success", description="Response status")
    message: str = Field(description="Response message")
    history: list[HistoryResponse] = Field(description="List of history records")
