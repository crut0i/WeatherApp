import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.utils import weather_utils
from app.core.decorators import require_auth
from app.core.connectors.db.sql.models import History
from app.core.models.weather import WeatherListResponse
from app.core.connectors.db.sql.repositories import HistoryRepository
from app.core.models.history import HistoryResponse, HistoryListResponse


class ServicesRoutes:
    """
    Services routes class
    """

    def __init__(self):
        self.router = APIRouter(tags=["Services Routes"])
        self.__set_routes()

    def __set_routes(self) -> None:
        """
        Services API routes
        """

        @self.router.get(
            "/weather/{city}",
            response_class=JSONResponse,
            status_code=200,
            description="Get weather for a city",
        )
        async def weather(city: str, request: Request):
            """
            Get weather for a city

            Returns:
                JSONResponse: Weather for a city
            """

            location = await weather_utils.get_location(city)
            if location is None:
                return JSONResponse(
                    status_code=404,
                    content={"status": "error", "message": "city not found"},
                )

            forecast = await weather_utils.get_weekly_forecast(location)
            response = WeatherListResponse(
                message=f"Weather for {city}",
                weather=forecast,
            )

            session_cookie = request.cookies.get("Session")

            if session_cookie:
                session_data = json.loads(session_cookie)
                session_id = session_data.get("session_id")

                await HistoryRepository().add(
                    History(
                        session_id=session_id,
                        city=city,
                        country=location.country,
                        latitude=location.latitude,
                        longitude=location.longitude,
                    )
                )

            return JSONResponse(
                status_code=200,
                content=response.model_dump(),
            )

        @self.router.get(
            "/history/{session_id}",
            response_class=JSONResponse,
            status_code=200,
            description="Get history",
        )
        @require_auth()
        async def history(session_id: str):
            """
            Get history
            """

            history = await HistoryRepository().get_history(session_id)
            if history is None:
                return JSONResponse(
                    status_code=404,
                    content={"status": "error", "message": "history not found"},
                )

            history_list = [
                HistoryResponse(
                    id=h.id,
                    session_id=h.session_id,
                    city=h.city,
                    country=h.country,
                    latitude=float(h.latitude),
                    longitude=float(h.longitude),
                )
                for h in history
            ]

            response = HistoryListResponse(
                message="history found",
                history=history_list,
            )

            return JSONResponse(
                status_code=200,
                content=response.model_dump(),
            )
