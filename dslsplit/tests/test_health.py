"""Testing the service."""
from fastapi.testclient import TestClient
from os import environ

environ["ENABLE_SECURITY"] = "false"
from dslsplit.app import app


client = TestClient(app)


def test_health() -> None:
    """Test healthcheck."""
    response = client.get("/health")
    assert response.status_code == 200
