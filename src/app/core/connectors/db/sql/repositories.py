from typing import Any
from sqlalchemy import select
from traceback import format_exc

from .connector import SQLConnector

from .models import Session, History
from app.core.connectors.logging import logger


class BaseRepository:
    """
    Base class for all repositories
    """

    def __init__(self):
        self._connector = SQLConnector()

    async def execute_query(self, query):
        """
        Execute SQLAlchemy query with proper session handling

        Args:
            query: SQLAlchemy query to execute

        Returns:
            Query result or None if error occurred
        """

        try:
            async with self._connector.session() as session:
                result = await session.execute(query)
                return result
        except Exception as e:
            logger.error(
                {
                    "service": "execute_query",
                    "message": "error executing query",
                    "error": str(e),
                    "traceback": format_exc(),
                }
            )
            return None

    async def add(self, instance) -> Any:
        """
        Add new instance to database

        Args:
            instance: SQLAlchemy model instance to add

        Returns:
            Added instance or None if error occurred
        """

        try:
            async with self._connector.session() as session:
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
                return instance
        except Exception as e:
            logger.error(
                {
                    "service": "add",
                    "message": "error adding instance",
                    "error": str(e),
                    "traceback": format_exc(),
                }
            )
            return None

    async def get(self, model, id: int) -> Any:
        """
        Get instance by id.

        Args:
            model: SQLAlchemy model class
            id: Instance ID

        Returns:
            Model instance or None if not found or error occurred
        """

        try:
            async with self._connector.session() as session:
                return await session.get(model, id)
        except Exception as e:
            logger.error(
                {
                    "service": "get",
                    "message": "error getting instance",
                    "error": str(e),
                    "traceback": format_exc(),
                }
            )
            return None

    async def list(self, model) -> list[Any]:
        """
        Get all instances of model.

        Args:
            model: SQLAlchemy model class

        Returns:
            List of model instances or empty list if error occurred
        """

        try:
            async with self._connector.session() as session:
                result = await session.execute(select(model))
                return result.scalars().all()
        except Exception as e:
            logger.error(
                {
                    "service": "list",
                    "message": "error listing instances",
                    "error": str(e),
                    "traceback": format_exc(),
                }
            )
            return []

    async def close(self) -> None:
        """
        Close current session
        """

        if self._session:
            try:
                await self._session.close()
            except Exception as e:
                logger.error(
                    {
                        "service": "close",
                        "message": "error closing session",
                        "error": str(e),
                        "traceback": format_exc(),
                    }
                )
            finally:
                self._session = None

    @property
    async def sql_session(self):
        """Get current session"""
        async with self._connector.session() as session:
            return session


class SessionRepository(BaseRepository):
    """
    Session repository
    """

    async def get_session(self, session_id: str) -> Session | None:
        """
        Get session by id.

        Args:
            session_id: Session ID

        Returns:
            Session instance or None if not found or error occurred
        """

        try:
            query = select(Session).where(Session.session_id == session_id)
            result = await self.execute_query(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                {
                    "service": "get_session",
                    "message": "error getting session",
                    "error": str(e),
                    "traceback": format_exc(),
                }
            )
            return None


class HistoryRepository(BaseRepository):
    """
    History repository
    """

    async def get_history(self, session_id: str) -> list[History] | None:
        """
        Get history by session id.

        Args:
            session_id: Session ID

        Returns:
            list[History] | None: List of history instances or None if error occurred
        """

        try:
            async with self._connector.session() as session:
                result = await session.execute(
                    select(History).where(History.session_id == session_id)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(
                {
                    "service": "get_history",
                    "message": "error getting history",
                    "error": str(e),
                    "traceback": format_exc(),
                }
            )
            return None
