"""Testing fastws exists service."""
import requests
from fastapi import status

from lextools import CONFIG
from lextools.easy_split import split_compound

HOST = f"http://{CONFIG.get('app', 'host')}:{CONFIG.get('app', 'port')}"


def test_splitter_service() -> None:
    """Test compound splitter API"""

    url = f"{HOST}/split"
    test_lemmas = ["operakoncert"]

    response = requests.get(url + f"/{test_lemmas[0]}")

    assert response.status_code == status.HTTP_200_OK

    json = response.json()
    assert json.keys() == {"word", "splits"}
    assert json["splits"][0].keys() == {"subtokens", "score", "fuge"}
    assert json["splits"][0]["subtokens"] == ["opera", "koncert"]
    assert isinstance(json["splits"][0]["score"], float)
    assert json["splits"][0]["score"] > 0.0
