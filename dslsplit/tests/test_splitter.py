"""Testing fastws exists service."""
import json
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from os import environ
from pathlib import Path

environ["ENABLE_SECURITY"] = "false"
from dslsplit.app import app
from dslsplit.train_splitter import train_splitter


client = TestClient(app)
current_dir = Path(__file__).parent.resolve()


def test_spliiter() -> None:
    """Test compound splitter API"""
    test_lemmas = ["operakoncert"]

    response = client.get("/split")

    # BAD TEST CASES
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # GOOD TEST CASES
    response = client.get(f"/split/{test_lemmas[0]}")

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    result["splits"][0]["score"] = ...
    assert result == {
        "word": "operakoncert",
        "splits": [
            {
                "subtokens": ["opera", "koncert"],
                "score": ...,
                "fuge": "",
            }
        ],
        "description": "",
        "method": "careful",
    }


def test_training_splitter() -> None:
    """Test training of compound splitter from file."""

    input_file = "lemma_liste_test.csv"
    input_file = str(current_dir / input_file)
    name = "test"
    delimiter = ";"
    columns = 0

    # test cannot find file
    with pytest.raises(FileNotFoundError):
        train_splitter("test.csv", name, force_training=True)

    # wrong delimiter
    with pytest.raises(ValueError):
        train_splitter(input_file, name, column=2, force_training=True)

    # wrong column
    with pytest.raises(ValueError):
        train_splitter(input_file, name, column="str", force_training=True)  # type: ignore

    prob_file = train_splitter(input_file, name, delimiter=delimiter, column=columns)

    # test output
    with open(prob_file) as f:
        ngram_probs = json.load(f)

    assert "prefix" in ngram_probs
    assert "suffix" in ngram_probs
    assert "infix" in ngram_probs

    assert len(ngram_probs.get("prefix", {}))
    assert len(ngram_probs.get("infix", {}))
    assert len(ngram_probs.get("suffix", {}))
