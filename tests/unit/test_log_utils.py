import json
import pytest

from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from src.app.core.utils.log import LogUtils


@pytest.fixture
def log_utils() -> LogUtils:
    """
    Create LogUtils instance for testing
    """
    return LogUtils()


@pytest.fixture
def sample_log_file(tmp_path: Path) -> Path:
    """
    Create a sample log file for testing
    """

    log_dir = tmp_path / "test_logs"
    log_dir.mkdir()
    log_file = log_dir / "log_2024-04-01.log"

    log_entries = [
        {"level": "INFO", "message": "Test info message"},
        {"level": "ERROR", "message": "Test error message"},
        {"level": "WARNING", "message": "Test warning message"},
        {"level": "DEBUG", "message": "Test debug message"},
    ]

    with open(log_file, "w", encoding="utf-8") as f:
        for entry in log_entries:
            f.write(json.dumps(entry) + "\n")

    return log_file


def test_get_available_dates(log_utils: LogUtils, tmp_path: Path) -> None:
    """
    Test getting available log dates
    """

    log_dir = tmp_path / "test_logs"
    log_dir.mkdir()

    (log_dir / "log_2024-04-01.log").touch()
    (log_dir / "log_2024-04-02.log").touch()
    (log_dir / "invalid.log").touch()

    with patch.object(log_utils, "_logs_dir", log_dir):
        dates = log_utils.get_available_dates()
        assert len(dates) == 2
        assert "2024-04-01" in dates
        assert "2024-04-02" in dates
        assert "invalid" not in dates


def test_get_log_content(log_utils: LogUtils, sample_log_file: Path) -> None:
    """
    Test getting log content
    """

    with patch.object(log_utils, "_logs_dir", sample_log_file.parent):
        content = log_utils.get_log_content("2024-04-01")

        assert content["date"] == "2024-04-01"
        assert content["total_entries"] == 4
        assert len(content["entries"]) == 4

        metadata = content["metadata"]
        assert metadata["error_count"] == 1
        assert metadata["info_count"] == 1
        assert metadata["warning_count"] == 1
        assert metadata["debug_count"] == 1


def test_get_log_content_not_found(log_utils: LogUtils, tmp_path: Path) -> None:
    """
    Test getting non-existent log content
    """

    log_dir = tmp_path / "test_logs"
    log_dir.mkdir()

    with patch.object(log_utils, "_logs_dir", log_dir):
        with pytest.raises(HTTPException) as exc_info:
            log_utils.get_log_content("2024-04-01")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "log file not found"


def test_delete_log(log_utils: LogUtils, sample_log_file: Path) -> None:
    """
    Test deleting log file
    """

    with patch.object(log_utils, "_logs_dir", sample_log_file.parent):
        result = log_utils.delete_log("2024-04-01")
        assert result["message"] == "log file for date 2024-04-01 deleted successfully"
        assert not sample_log_file.exists()


def test_delete_log_not_found(log_utils: LogUtils, tmp_path: Path) -> None:
    """
    Test deleting non-existent log file
    """

    log_dir = tmp_path / "test_logs"
    log_dir.mkdir()

    with patch.object(log_utils, "_logs_dir", log_dir):
        with pytest.raises(HTTPException) as exc_info:
            log_utils.delete_log("2024-04-01")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "log file not found"
