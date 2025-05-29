import httpx

from app.core.connectors.config import config
from app.core.models.weather import LocationInfo, WeatherResponse, DailyForecast


class WeatherUtils:
    def __init__(self):
        self.openmeteo_api_url = config.openmeteo_api_url
        self.openmeteo_geocoding_api_url = config.openmeteo_geocoding_api_url

    async def get_location(self, city_name: str) -> LocationInfo | None:
        params = {"name": city_name, "count": 1, "language": "en", "format": "json"}

        async with httpx.AsyncClient() as client:
            response = await client.get(self.openmeteo_geocoding_api_url + "/search", params=params)
            response.raise_for_status()
            data = response.json()

        if not data.get("results"):
            return None

        result = data["results"][0]
        return LocationInfo(
            name=result["name"],
            country=result["country"],
            latitude=result["latitude"],
            longitude=result["longitude"],
        )

    async def get_weekly_forecast(self, location: LocationInfo) -> WeatherResponse:
        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "daily": "temperature_2m_max,temperature_2m_min,weathercode",
            "timezone": "auto",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.openmeteo_api_url + "/forecast", params=params)
            response.raise_for_status()
            data = response.json()

        forecasts = [
            DailyForecast(
                date=data["daily"]["time"][i],
                temperature_max=data["daily"]["temperature_2m_max"][i],
                temperature_min=data["daily"]["temperature_2m_min"][i],
                weather_code=data["daily"]["weathercode"][i],
            )
            for i in range(len(data["daily"]["time"]))
        ]

        return WeatherResponse(
            latitude=location.latitude,
            longitude=location.longitude,
            city=location.name,
            country=location.country,
            daily=forecasts,
        )
