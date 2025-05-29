from typing import Any
from traceback import format_exc
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.connectors.config import config
from app.core.connectors.logging import logger


Base = declarative_base()


class SQLConnector:
    """
    SQL connector
    """

    def __init__(self):
        self.engine = create_async_engine(
            url=config.db_url, echo=False, pool_pre_ping=True, pool_size=20, max_overflow=10
        )
        self.session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        self.Base = Base

    def get_session(self) -> AsyncSession:
        """
        Get a new database session

        Returns:
            AsyncSession: Database session
        """

        return self.session()

    async def execute(self, query) -> Any:
        """Execute SQLAlchemy query

        Args:
            query: SQLAlchemy query to execute

        Returns:
            Any: Query result
        """

        try:
            async with self.session() as session:
                result = await session.execute(query)
                await session.commit()
                return result
        except Exception as e:
            logger.error(
                {
                    "service": "sql execute",
                    "query": query,
                    "message": "error executing sql query",
                    "error": str(e),
                    "traceback": format_exc(),
                }
            )
            return None
