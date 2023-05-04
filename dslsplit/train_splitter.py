import argparse
import os
import tempfile
import json
import pandas as pd
from charsplit import training
from pathlib import Path

current_dir = Path(__file__).parent.resolve()


def argparser():
    """Handle command-line arguments."""
    parser = argparse.ArgumentParser(
        description="""Calculate ngram probabilities for compound splitter"""
    )
    parser.add_argument("--input_file", "-i", help="Lemma list input file")
    parser.add_argument(
        "--name", "-n", help="name for output subset. Will save at [NAME]_prob.json"
    )
    parser.add_argument("--lang", help="language")
    parser.add_argument("--delimiter", help="delimiter used in input file", default=",")
    parser.add_argument("--col", help="lemma column placement in input file", default=0)
    return parser.parse_args()


def train_splitter(
    lemma_file: str,
    output_name: str,
    output_dir: str = "",
    lang: str = "da",
    delimiter: str = ",",
    column: int = 0,
    force_training: bool = False,
) -> str:
    probality_file = f"{lang}_{output_name}_prob.json"
    if not output_dir:
        probality_file = os.path.join(tempfile.gettempdir(), probality_file)
    # If file exists, we assume it is already trained
    if not force_training and os.path.isfile(probality_file):
        print(f"File {probality_file} already exists. Skipping training.")
        return probality_file

    if not isinstance(delimiter, str):
        delimiter = str(delimiter)

    if not isinstance(column, int):
        column = int(column)

    if not lemma_file[0] in ("~", "/", "\\"):
        lemma_file = str(current_dir / lemma_file)
    if not os.path.exists(lemma_file):
        raise FileNotFoundError(f"Cannot find file {lemma_file}")
    lemmas = pd.read_csv(lemma_file, sep=delimiter, usecols=[column], names=["lemma"])
    lemmas = (
        lemmas.lemma.drop_duplicates().astype(str).values
    )  # remove duplicates and return as array
    length = len(lemmas)

    if not length:  # assume its an error if no full forms can be found
        raise ValueError(
            f"Cannot process full forms in {lemma_file} "
            f"with delimiter '{delimiter}' and column '{column}"
        )

    with tempfile.TemporaryDirectory() as td:  # tmp dir as windows cant reopen a tmp file
        f_name = os.path.join(td, "test")
        with open(f_name, "w", encoding="utf8") as fh:
            for form in lemmas:
                fh.write(form + "\n")

        # language "da" is hardkodet into the name for now
        training.main(f_name, probality_file, max_words=length)

        # CharSplit saves the file with utf-8 encoding, but with ascii characters
        # We redo the save with ensure_ascii=False to get the correct encoding
        with open(probality_file) as f:
            ngram_probs = json.load(f)
        with open(probality_file, "w") as f:
            str_version = json.dumps(ngram_probs, ensure_ascii=False)
            f.write(str_version)
    return probality_file


if __name__ == "__main__":
    ARGS = argparser()

    input_file = ARGS.input_file
    name = ARGS.name
    language = ARGS.lang  # todo: define acceptable input lang + check
    delim = ARGS.delimiter
    col = int(ARGS.col)

    train_splitter(input_file, name, lang=language, delimiter=delim, column=col)
