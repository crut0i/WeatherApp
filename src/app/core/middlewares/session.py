import uuid
import json

from collections.abc import Callable
from fastapi import Request, Response
from datetime import datetime, timedelta, UTC
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.connectors.db.sql import session_repo
from app.core.connectors.db.sql.models import Session


class SessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle session management
    """

    def __init__(self, app, session_cookie_name: str = "Session", session_expiry_days: int = 7):
        super().__init__(app)
        self.__session_cookie_name = session_cookie_name
        self.__session_expiry_days = session_expiry_days

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Dispatch

        Args:
            request (Request): Request object
            call_next (Callable): Callable

        Returns:
            Response: Response object
        """

        session_cookie = request.cookies.get(self.__session_cookie_name)
        if session_cookie:
            try:
                session_data = json.loads(session_cookie)
                expiry_date = datetime.fromisoformat(session_data.get("expiry"))

                if expiry_date > datetime.now(UTC) and await session_repo.get_session(
                    session_data.get("session_id")
                ):
                    request.state.session_id = session_data.get("session_id")
                    response = await call_next(request)
                    return response

                request.cookies.clear()
            except (json.JSONDecodeError, ValueError, TypeError):
                pass

        session_id = str(uuid.uuid4())
        expiry_date = datetime.now(UTC) + timedelta(days=self.__session_expiry_days)

        session_data = {"session_id": session_id, "expiry": expiry_date.isoformat()}

        await session_repo.add(Session(session_id=session_id, user_ip=request.state.client_ip))

        response = await call_next(request)

        response.set_cookie(
            key=self.__session_cookie_name,
            value=json.dumps(session_data),
            expires=expiry_date,
            httponly=True,
            secure=True,
            samesite="strict",
        )

        return response
