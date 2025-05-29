import hvac

from traceback import format_exc

from app.core.connectors.config import config
from app.core.connectors.logging import logger


class VaultClient:
    """
    HashiCorp Vault client
    """

    def __init__(self):
        vault_addr = config.vault_addr
        self.__client = hvac.Client(url=vault_addr)

        self.__client.auth.approle.login(
            role_id=config.vault_role_id.get_secret_value(),
            secret_id=config.vault_secret_id.get_secret_value(),
        )

        if not self.__client.is_authenticated():
            logger.error({"type": "vault", "error": "authentication failed"})
            raise Exception("Vault authentication failed")

    def get_secret(self, path: str, key: str) -> str:
        """
        Get a secret from Vault

        Args:
            path (str): Path to the secret
            key (str): Key of the secret

        Raises:
            Exception: If the secret is not found

        Returns:
            str: Secret value
        """

        try:
            result = self.__client.secrets.kv.v2.read_secret_version(
                mount_point="kv", path=path, raise_on_deleted_version=True
            )
            return result["data"]["data"][key]
        except Exception as e:
            logger.error({"type": "vault", "error": str(e), "traceback": format_exc()})
            raise e
