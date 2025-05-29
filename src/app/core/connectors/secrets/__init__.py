from .client import VaultClient

_vault_instance: VaultClient | None = None

def get_vault() -> VaultClient:
    global _vault_instance
    if _vault_instance is None:
        _vault_instance = VaultClient()
    return _vault_instance
