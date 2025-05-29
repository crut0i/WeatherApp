from pydantic import BaseModel, Field


class DailyForecast(BaseModel):
    """
    Daily forecast model
    """

    date: str = Field(description="Forecast date")
    temperature_max: float = Field(description="Maximum temperature in Celsius")
    temperature_min: float = Field(description="Minimum temperature in Celsius")
    weather_code: int = Field(description="Weather code")


class WeatherResponse(BaseModel):
    """
    Weather response model
    """

    latitude: float = Field(description="Location latitude")
    longitude: float = Field(description="Location longitude")
    city: str = Field(description="City name")
    country: str = Field(description="Country name")
    daily: list[DailyForecast] = Field(description="List of daily forecasts")


class WeatherListResponse(BaseModel):
    """
    Weather list response model
    """

    status: str = Field(default="success", description="Response status")
    message: str = Field(description="Response message")
    weather: WeatherResponse = Field(description="Weather data")


class LocationInfo(BaseModel):
    """
    Location info model
    """

    name: str = Field(description="Location name")
    country: str = Field(description="Country name")
    latitude: float = Field(description="Location latitude")
    longitude: float = Field(description="Location longitude")
