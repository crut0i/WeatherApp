import pytest

from fastapi import status


@pytest.mark.asyncio
async def test_routes(client):
    """
    Ping test
    """
    response = client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK
