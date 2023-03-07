"""Testing fastws exists service."""
import os
import requests
from fastapi import status

from lextools import CONFIG


HOST = f"http://{CONFIG.get('app', 'host')}:{CONFIG.get('app', 'port')}"
RESPONSE_KEYS = {"word", "splits", "description", "method"}


def test_splitter_service() -> None:
    """Test compound splitter API"""

    url = f"{HOST}/split"
    test_lemmas = ["operakoncert"]

    response = requests.get(url + f"/{test_lemmas[0]}")

    assert response.status_code == status.HTTP_200_OK

    json = response.json()
    assert json.keys() == RESPONSE_KEYS
    assert json["splits"][0].keys() == {"subtokens", "score", "fuge"}
    assert json["splits"][0]["subtokens"] == ["opera", "koncert"]
    assert isinstance(json["splits"][0]["score"], float)
    assert json["splits"][0]["score"] > 0.0


def test_mixed_method() -> None:
    """Test the mixed method."""

    url = f"{HOST}/split"
    lemma_no_careful_split = "badeand"

    for method in ("mixed", "careful", "brute"):
        response_method = "brute" if method == "mixed" else method
        response = requests.get(
            os.path.join(url, f"{lemma_no_careful_split}?method={method}")
        )
        json = response.json()
        assert json.keys() == RESPONSE_KEYS
        assert json["method"] == response_method
