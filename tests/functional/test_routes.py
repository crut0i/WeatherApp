import pytest

from fastapi import status
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
@patch("app.core.utils.log_utils.get_available_dates")
@patch("app.core.connectors.db.redis.redis_connector.get", new_callable=AsyncMock)
@patch("app.core.connectors.db.redis.redis_connector.setex", new_callable=AsyncMock)
@patch("app.core.connectors.db.redis.redis_connector.exists", new_callable=AsyncMock)
async def test_logs_list_endpoint(
    mock_redis_exists, mock_redis_setex, mock_redis_get, mock_get_dates, client
) -> None:
    """Test logs list endpoint"""
    dates = ["2024-04-01", "2024-04-02"]
    mock_get_dates.return_value = dates
    mock_redis_get.return_value = None
    mock_redis_setex.return_value = True
    mock_redis_exists.return_value = False

    response = client.get("/api/logs")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "success", "dates": dates}


@pytest.mark.asyncio
@patch("app.core.utils.log_utils.get_log_content")
async def test_get_log_content_endpoint(mock_get_content, client) -> None:
    """
    Test get log content endpoint
    """

    test_date = datetime.now().strftime("%Y-%m-%d")
    mock_content = {"content": "test log content"}
    mock_get_content.return_value = mock_content

    response = client.get(f"/api/logs/{test_date}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_content


@pytest.mark.asyncio
@patch("app.core.utils.log_utils.delete_log")
@patch("app.core.connectors.db.redis.redis_connector.delete", new_callable=AsyncMock)
async def test_delete_log_endpoint(mock_redis_delete, mock_delete_log, client) -> None:
    """
    Test delete log endpoint with past date
    """
    test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    expected_response = {
        "status": "success",
        "message": f"log file for date {test_date} deleted successfully",
    }
    mock_delete_log.return_value = expected_response
    mock_redis_delete.return_value = True

    response = client.delete(f"/api/logs/{test_date}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response


@pytest.mark.asyncio
@patch("app.core.utils.log_utils.delete_log")
async def test_delete_current_day_log_endpoint(mock_delete_log, client) -> None:
    """
    Test delete log endpoint with current date
    Should return error
    """

    test_date = datetime.now().strftime("%Y-%m-%d")
    mock_delete_log.return_value = {"status": "success"}

    response = client.delete(f"/api/logs/{test_date}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"status": "error", "detail": "cannot delete logs for current day"}


@pytest.mark.asyncio
async def test_weather_success(client):
    response = client.get("/api/v1/weather/Moscow")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "weather" in data
    assert data["weather"]["city"].lower() == "moscow"
    assert "daily" in data["weather"]
    assert isinstance(data["weather"]["daily"], list)


@pytest.mark.asyncio
async def test_weather_not_found(client):
    response = client.get("/api/v1/weather/non_existent_city")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "city not found"
