import argparse
import os
import tempfile

import pandas as pd
from charsplit import training


def argparser():
    """Handle command-line arguments."""
    parser = argparse.ArgumentParser(description="""Calculate ngram probabilities for compound splitter""")
    parser.add_argument("--input_file", "-i", help="Full form word list input file")
    parser.add_argument("--name", "-n", help="name for output subset. Will save at [NAME]_prob.json")
    parser.add_argument("--delimiter", help="delimiter used in input file", default=",")
    parser.add_argument("--col", help="full form column placement in input file", default=0)
    return parser.parse_args()


def train_splitter(full_form_file: str, output_name: str, delimiter: str = ",", column: int = 0) -> None:
    if not isinstance(delimiter, str):
        delimiter = str(delimiter)

    if not isinstance(column, int):
        column = int(column)

    full_forms = pd.read_csv(full_form_file, sep=delimiter, usecols=[column], names=['full_form'])
    full_forms = full_forms.full_form.drop_duplicates().astype(str).values  # remove duplicates and return as array
    length = len(full_forms)

    if not length:  # assume its an error if no full forms can be found
        raise ValueError(f"Cannot process full forms in {full_form_file} "
                         f"with delimiter '{delimiter}' and column '{column}")

    with tempfile.TemporaryDirectory() as td:  # tmp dir as windows cant reopen a tmp file
        f_name = os.path.join(td, "test")
        with open(f_name, "w", encoding="utf8") as fh:
            for form in full_forms:
                fh.write(form + '\n')

        # language "da" is hardkodet into the name for now
        training.main(f_name, f"da_{output_name}_prob.json", max_words=length)


if __name__ == "__main__":
    ARGS = argparser()

    input_file = ARGS.input_file
    name = ARGS.name
    delim = ARGS.delimiter
    col = int(ARGS.col)

    train_splitter(input_file, name, delim, col)
