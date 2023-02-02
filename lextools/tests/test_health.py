"""Testing fastws exists service."""
import pytest
import requests


HOST = "http://127.0.0.1:8000"


def test_health() -> None:
    """Test healthcheck."""
    url = f"{HOST}/health"
    response = requests.get(url)
    assert response.status_code == 200


# @pytest.mark.parametrize("index", INDICES)
# def test_alive(index) -> None:
#     """Test basic exists functionality."""
#     query = "husar"
#     url = f"{HOST}/{SERVICE}/{index}/{query}?api-key={API_KEY}"
#     response = requests.get(url)
#     assert response.status_code == 200
