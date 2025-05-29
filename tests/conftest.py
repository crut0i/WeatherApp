import os
import sys
import pytest

from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

"""
Pytest pre-run configuration
"""

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "src"))

os.environ["USE_TEST_CONFIG"] = "1"

from src.app.core.connectors.config import config  #  noqa
from src.app.core.api.main.routes import main_routes  #  noqa
from src.app.core.api.v1.routes import services_routes  #  noqa


@pytest.fixture(scope="session")
def app():
    """
    Create FastAPI application instance
    """

    app = FastAPI(title="Test API")

    default_router = APIRouter(prefix="/api")
    api_router = APIRouter(prefix="/api/" + config.api_prefix)

    default_router.include_router(main_routes.router)
    api_router.include_router(services_routes.router)

    app.include_router(router=default_router)
    app.include_router(router=api_router)

    return app


@pytest.fixture(scope="session")
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_request_state():
    """Mock request state for tests"""
    with patch("fastapi.Request.state") as mock_state:
        mock_state.request_id = "test_request_id"
        mock_state.client_ip = "127.0.0.1"
        yield mock_state


@pytest.fixture(autouse=True, scope="session")
def patch_vault():
    """
    Prevent real VaultClient() creation during tests
    """

    with patch("app.core.connectors.secrets.client.VaultClient") as vault_mock_cls:
        vault_mock = MagicMock()
        vault_mock.get_secret.return_value = "test"
        vault_mock_cls.return_value = vault_mock
        yield
