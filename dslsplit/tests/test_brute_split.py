"""Testing fastws brute split and mixed mode."""
from fastapi import status
from fastapi.testclient import TestClient
from os import environ

environ["ENABLE_SECURITY"] = "false"
environ["FASTAPI_SIMPLE_SECURITY_API_KEY_FILE"] = ""
from dslsplit.app import app

client = TestClient(app)

RESPONSE_KEYS = {"word", "splits", "description", "method"}


def test_splitter_service() -> None:
    """Test compound splitter API"""

    test_lemmas = ["operakoncert"]
    response = client.get(f"/split/{test_lemmas[0]}")

    assert response.status_code == status.HTTP_200_OK

    json = response.json()
    assert json.keys() == RESPONSE_KEYS
    assert json["splits"][0].keys() == {"subtokens", "score", "fuge"}
    assert json["splits"][0]["subtokens"] == ["opera", "koncert"]
    assert isinstance(json["splits"][0]["score"], float)
    assert json["splits"][0]["score"] > 0.0


def test_mixed_method() -> None:
    """Test the mixed method."""

    lemma_no_careful_split = "badeand"

    for method in ("mixed", "careful", "brute"):
        response_method = "brute" if method == "mixed" else method
        response = client.get(f"/split/{lemma_no_careful_split}?method={method}")
        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json.keys() == RESPONSE_KEYS
        assert json["method"] == response_method
