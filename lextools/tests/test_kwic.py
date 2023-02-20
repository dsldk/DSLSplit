"""Testing fastws exists service."""
import json

import pytest
import requests
from fastapi import status


HOST = "http://127.0.0.1:8000"


def test_kwic() -> None:
    """Test kwic concordance API"""

    url = f"{HOST}/concordance"
    test_queries = ["+visiteret +(akutfunktion|akutfunktionen|akutfunktioner|akutfunktionerne)"]

    response = requests.get(url)

    # BAD TEST CASES
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # GOOD TEST CASES
    response = requests.get(url + f"?query={test_queries[0]}")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {"lemma": "operakoncert",
                               "subtokens": [["opera", "koncert"]],
                               "scores": [0.09712350339086326]
                               }