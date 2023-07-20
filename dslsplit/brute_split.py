import os
import pickle
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any

from dslsplit import CONFIG, logger, timeit

current_dir = Path(__file__).parent.resolve()


@timeit
def train_splitter(data: list) -> Dict[str, float]:
    """Train the splitter.

    Args:
        data: List of compounds to train the splitter on.

    Returns:
        Dictionary of ngram probabilities."""
    # Count character pentagrams
    trigram_counts = defaultdict(int)
    for compound in data:
        split_compound = f"$${compound}__"
        for i in range(2, len(split_compound) - 2):
            trigram = split_compound[i - 2 : i + 3]
            trigram_counts[trigram] += 1

    # Calculate trigram probabilities
    probabilities = {}
    total_trigrams = sum(trigram_counts.values())
    for trigram, count in trigram_counts.items():
        probabilities[trigram] = count / total_trigrams

    return probabilities


@timeit
def load_probabilities(force_training: bool = False) -> Dict[str, Dict[str, float]]:
    """Load the trigram probabilities.

    Args:
        force_training: If True, don't use any previous training.

    Returns:
        Dictionary with probabilities with each language variant as key."""
    variants = CONFIG.get("brute", "variants")
    result = {}
    for variant in variants.split(","):
        variant = variant.strip()
        # Try to unpickle trigram probabilities. If that fails, train the splitter
        # and pickle the trigram probabilities.
        pickle_file = os.path.join(
            tempfile.gettempdir(), f"brute_split_probs_{variant}.pickle"
        )

        if not force_training:
            try:
                with open(pickle_file, "rb") as f:
                    probabilities = pickle.load(f)
                logger.info(f"Probabilities loaded from {pickle_file}")
                result[variant] = probabilities
                continue
            except FileNotFoundError:
                logger.info("Probabilities not found. Training the splitter...")

        data_files = CONFIG.get(f"brute_{variant}", "data_files").split(",")
        data_files = [item.split(":") for item in data_files]

        data = []
        for data_file, preprocess_method in data_files:
            filepath = current_dir / data_file
            with open(filepath, "r") as f:
                data += preprocess_data(f.read().splitlines(), preprocess_method)
        data = list(set(data))
        probabilities = train_splitter(data)
        with open(pickle_file, "wb") as f:
            pickle.dump(probabilities, f)
        result[variant] = probabilities

    return result


def preprocess_data(data: List[str], todo: str = "") -> List[str]:
    """Preprocess the data using specification in config file.

    Args:
        data: List of compounds to preprocess.
        todo: What to do with the data. Options are: modernize_danish.
    Returns:
        List of preprocessed compounds
    """
    output = []
    for line in data:
        if todo == "modernize_danish":
            # Get all values from CONFIG
            replacements = CONFIG.get("brute_modernize_danish", "replacements").split(
                ","
            )
            replacements = [item.split(":") for item in replacements]
            for old, new in replacements:
                line = line.replace(old, new)
        output.append(line)
    return output


# @timeit
def split_compound(
    compound: str, probabilities: Dict[str, float]
) -> Dict[str, str | List[Dict[str, str | float | List[str]]]]:
    """Split a compound word using probability dictionary.

    Args:
        compound: The compound word to split.
        probabilities: Dictionary of ngram probabilities.

    Returns:
        Dictionary with the following keys: word, splits, description, method.
    """
    # If a ngram is not in the ngram probability dictionary, assume a very low probability
    very_low_probability = 1e-20
    low_probability = 1e-10
    large_probability = 1

    # Generate list of candidates
    candidates = []
    # Add candidates with plus sign between each character
    for i in range(1, len(compound)):
        candidate = compound[:i] + "+" + compound[i:]
        candidates.append(candidate)
    # Add candidates with plus sign on both sides of s and e
    for i in range(1, len(compound) - 1):
        if compound[i] == "s" and compound[i - 1] != "+" and compound[i + 1] != "+":
            candidate = compound[:i] + "+s+" + compound[i + 1 :]
            candidates.append(candidate)
        elif compound[i] == "e" and compound[i - 1] != "+" and compound[i + 1] != "+":
            candidate = compound[:i] + "+e+" + compound[i + 1 :]
            candidates.append(candidate)
        elif compound[i] == "-" and compound[i - 1] != "+" and compound[i + 1] != "+":
            candidate = compound[:i] + "+-+" + compound[i + 1 :]
            candidates.append(candidate)

    # Calculate scores for each candidate
    scores = []
    for candidate in candidates:
        print("====", candidate, "====")
        pentagrams_not_found = 0
        score = 1
        split_compound = "$$" + candidate + "__"
        center_position = len(split_compound) / 2
        for i in range(2, len(split_compound) - 2):
            pentagram = split_compound[i - 2 : i + 3]
            if "+" not in pentagram:
                continue
            if not pentagram in probabilities and "+-+" not in pentagram:
                pentagrams_not_found += 1
            if "+-+" in pentagram or pentagram[0:2] == "-+" or pentagram[-2:] == "+-":
                penta_prob = large_probability
            elif pentagram in probabilities:
                penta_prob = probabilities[pentagram]
            elif "$" in pentagram or "_" in pentagram:
                penta_prob = very_low_probability
            else:
                penta_prob = low_probability

            # Penalize pentagrams that are close to the beginning or end of the word
            position_score = 1 - abs(i - center_position) / center_position
            penta_prob *= position_score**2
            print(pentagram, position_score, penta_prob)
            score *= penta_prob

        if pentagrams_not_found == 5:
            score = 0.0
        print("Score:", score)
        scores.append(score)

    # Combine candidates with their scores
    results = list(zip(candidates, scores))
    # Remove candidates with 0.0 probability
    results = [x for x in results if x[1] > 0]
    # Sort results in descending order by score
    results.sort(key=lambda x: x[1], reverse=True)

    output = {}
    output["word"] = compound
    output["splits"] = []
    for candidate, score in results:
        split = candidate.split("+")
        joint_element = split[1] if len(split) > 2 else ""
        output["splits"].append(
            {"subtokens": [split[0], split[-1]], "fuge": joint_element, "score": score}
        )
        if len(split) > 3:
            logger.warning(f"More than 3 splits for {compound}: {split}!")

    return output


if __name__ == "__main__":
    probabilities = load_probabilities(force_training=True)
    # Split the words
    WORDS = [
        "askeskyen",
        "askesky",
        "skaderede",
        "skaderer",
        "skaderes",
        "skaderet",
        "skaderne",
        "skadesanmeldelse",
        "husarbejde",
        "sengekant",
        "operakoncert",
        "badeland",
        "badeand",
        "trækvinden",
        "sneboldkamp",
        "skrivebordslampe",
        "ålefiskeri",
        "rotavirus",
        "adgangsportal",
        "karrierevalg",
        "skovsnegl",
        "ihændehaver",
    ]
    for variant in ("nudansk", "yngrenydansk"):
        print("=======")
        print(variant)
        for word in WORDS:
            print(word, split_compound(word, probabilities[variant]))
