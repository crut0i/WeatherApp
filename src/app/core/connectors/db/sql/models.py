from traceback import format_exc
from sqlalchemy import Column, BigInteger, Text, Numeric, ForeignKey

from app.core.connectors.logging import logger
from app.core.connectors.db.sql.connector import Base, SQLConnector


class Session(Base):
    """
    Session model for managing session information and permissions

    Attributes:
        id: Primary key
        session_id: Session ID
        user_ip: User IP address
    """

    __tablename__ = "sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(Text, nullable=False, unique=True)
    user_ip = Column(Text, nullable=False)

    def __repr__(self):
        return f"Session(id={self.id}, session_id='{self.session_id}', user_ip='{self.user_ip}')"


class History(Base):
    """
    History model for storing user search history

    Attributes:
        id: Primary key
        session_id: Session ID
        city: City name
        country: Country name
        latitude: Latitude
        longitude: Longitude
    """

    __tablename__ = "history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(Text, ForeignKey("sessions.session_id"))
    city = Column(Text, nullable=False)
    country = Column(Text, nullable=False)
    latitude = Column(Numeric, nullable=False)
    longitude = Column(Numeric, nullable=False)

    def __repr__(self):
        return f"History(id={self.id}, session_id='{self.session_id}'"


async def init_models() -> None:
    """
    Initialize database by creating all defined tables
    """

    __connector = SQLConnector()

    try:
        async with __connector.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    except Exception as e:
        logger.error(
            {
                "service": "sql execute",
                "message": "error while initializing models",
                "error": str(e),
                "traceback": format_exc(),
            }
        )
        raise
