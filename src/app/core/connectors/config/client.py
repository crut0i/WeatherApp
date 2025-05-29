import os

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings class for handling application configuration
    """

    # Paths
    log_path: str

    # Redis config
    redis_host: str
    redis_port: str

    # Loki config
    loki_endpoint: str

    # Vault config
    vault_addr: str
    vault_role_id: SecretStr
    vault_secret_id: SecretStr

    # API preferences
    api_prefix: str

    # DB config
    db_host: str
    db_port: str
    db_name: str | None = None
    db_username: SecretStr | None = None
    db_password: SecretStr | None = None

    # External services
    openmeteo_api_url: str
    openmeteo_geocoding_api_url: str

    # Frontend
    frontend_path: str

    # App mode
    app_mode: str = "production"

    @property
    def docs_url(self) -> str:
        return None if self.app_mode == "production" else "/docs"

    @property
    def redoc_url(self) -> str:
        return None if self.app_mode == "production" else "/redoc"

    @property
    def openapi_url(self) -> str:
        return None if self.app_mode == "production" else "/openapi.json"

    @property
    def db_url(self) -> str:
        """
        Get the database URL

        Returns:
            str: Database URL
        """

        if os.getenv("USE_TEST_CONFIG") == "1":
            db_username = "test"
            db_password = "test"
            db_name = "test"
        else:
            from app.core.connectors.secrets import get_vault  # noqa

            vault = get_vault()
            db_username = vault.get_secret("db", "db_username")
            db_password = vault.get_secret("db", "db_password")
            db_name = vault.get_secret("db", "db_name")

        return f"postgresql+asyncpg://{db_username}:{db_password}@{self.db_host}:{self.db_port}/{db_name}"

    @property
    def auth_token(self) -> str:
        """
        Get the authorization token

        Returns:
            str: Authorization token
        """

        if os.getenv("USE_TEST_CONFIG") != "1":
            from app.core.connectors.secrets import get_vault

            vault = get_vault()
            auth_token = vault.get_secret("access/authorization", "token")
        else:
            auth_token = "test"
        return auth_token

    model_config = SettingsConfigDict(
        env_file="tests/.env.test" if os.getenv("USE_TEST_CONFIG") == "1" else "config/.env",
        env_file_encoding="utf-8",
    )
