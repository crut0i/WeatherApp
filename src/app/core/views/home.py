from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates

from app.core.connectors.config import config


class HomeRoutes:
    """
    Home routes class
    """

    def __init__(self):
        self.router = APIRouter(tags=["Home Routes"])
        self.templates = Jinja2Templates(directory=config.templates_path)
        self.__set_routes()

    def __set_routes(self) -> None:
        """
        Home API routes
        """

        @self.router.get("/", include_in_schema=False)
        async def home(request: Request):
            """
            Home page
            """

            return self.templates.TemplateResponse("index.html", {"request": request})
