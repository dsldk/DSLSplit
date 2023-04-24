"""Testing fastws exists service."""
import pytest
import requests

HOST = "http://127.0.0.1:8000"


def test_health() -> None:
    """Test healthcheck."""
    url = f"{HOST}/health"
    response = requests.get(url)
    assert response.status_code == 200
