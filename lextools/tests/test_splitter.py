"""Testing fastws exists service."""
import json

import pytest
import requests
from fastapi import status
from lextools.train_splitter import train_splitter

HOST = "http://127.0.0.1:8000"


def test_spliiter() -> None:
    """Test compound splitter API"""

    url = f"{HOST}/split"
    test_lemmas = ["operakoncert"]

    response = requests.get(url)

    # BAD TEST CASES
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # GOOD TEST CASES
    response = requests.get(url + f"/{test_lemmas[0]}")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {"lemma": "operakoncert",
                               "subtokens": [["opera", "koncert"]],
                               "scores": [0.09712350339086326]
                               }


def test_training_splitter() -> None:
    """Test training of compound splitter from file."""

    input_file = "lemma_liste_test.csv"
    name = "test"
    delimiter = ";"
    columns = 0

    # test cannot find file
    with pytest.raises(FileNotFoundError):
        train_splitter("test.csv", name)

    # wrong delimiter
    with pytest.raises(ValueError):
        train_splitter(input_file, name, column=2)

    # wrong column
    with pytest.raises(ValueError):
        train_splitter(input_file, name, column="str")

    train_splitter(input_file, name, delimiter=delimiter, column=columns)

    # test output
    with open(f"da_{name}_prob.json") as f:
        ngram_probs = json.load(f)

    assert "prefix" in ngram_probs
    assert "suffix" in ngram_probs
    assert "infix" in ngram_probs

    assert len(ngram_probs.get("prefix", {}))
    assert len(ngram_probs.get("infix", {}))
    assert len(ngram_probs.get("suffix", {}))





