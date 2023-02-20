import argparse
import os
import tempfile
import json
import pandas as pd
from charsplit import training


def argparser():
    """Handle command-line arguments."""
    parser = argparse.ArgumentParser(description="""Calculate ngram probabilities for compound splitter""")
    parser.add_argument("--input_file", "-i", help="Lemma list input file")
    parser.add_argument("--name", "-n", help="name for output subset. Will save at [NAME]_prob.json")
    parser.add_argument("--lang", help="language")
    parser.add_argument("--delimiter", help="delimiter used in input file", default=",")
    parser.add_argument("--col", help="lemma column placement in input file", default=0)
    return parser.parse_args()


def train_splitter(lemma_file: str, output_name: str,
                   lang: str = "da", delimiter: str = ",", column: int = 0) -> None:
    if not isinstance(delimiter, str):
        delimiter = str(delimiter)

    if not isinstance(column, int):
        column = int(column)

    lemmas = pd.read_csv(lemma_file, sep=delimiter, usecols=[column], names=['lemma'])
    lemmas = lemmas.lemma.drop_duplicates().astype(str).values  # remove duplicates and return as array
    length = len(lemmas)

    if not length:  # assume its an error if no full forms can be found
        raise ValueError(f"Cannot process full forms in {lemma_file} "
                         f"with delimiter '{delimiter}' and column '{column}")

    with tempfile.TemporaryDirectory() as td:  # tmp dir as windows cant reopen a tmp file
        f_name = os.path.join(td, "test")
        with open(f_name, "w", encoding="utf8") as fh:
            for form in lemmas:
                fh.write(form + '\n')

        # language "da" is hardkodet into the name for now
        training.main(f_name, f"{lang}_{output_name}_prob.json", max_words=length)

        with open(f"{lang}_{output_name}_prob.json") as f:
            ngram_probs = json.load(f)
        with open(f"{lang}_{output_name}_prob.json", "w") as f:
            str_version = json.dumps(ngram_probs, ensure_ascii=False)
            f.write(str_version)


if __name__ == "__main__":
    ARGS = argparser()

    input_file = ARGS.input_file
    name = ARGS.name
    language = ARGS.lang  # todo: define acceptable input lang + check
    delim = ARGS.delimiter
    col = int(ARGS.col)

    train_splitter(input_file, name, language, delim, col)
