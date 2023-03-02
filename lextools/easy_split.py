import logging
import pickle
import tempfile
from collections import defaultdict

from lextools import CONFIG

logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

import time
from functools import wraps


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"{func.__name__} took {end - start:.6f} seconds to complete")
        return result

    return wrapper


@timeit
def train_splitter(data: list) -> dict:
    """Train the splitter"""
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
def load_probabilities() -> dict:
    """Load the trigram probabilities."""
    # Try to unpickle trigram probabilities. If that fails, train the splitter
    # and pickle the trigram probabilities.
    pickle_file = tempfile.gettempdir() + "/easysplit_probs.pickle"
    try:
        with open(pickle_file, "rb") as f:
            probalities = pickle.load(f)
        logger.info(f"Probabilities loaded from {pickle_file}")
    except FileNotFoundError:
        logger.info("Probabilities not found. Training the splitter...")
        data_file = CONFIG.get("easy_split", "data_file")
        with open(data_file, "r") as f:
            data = f.read().splitlines()
            probalities = train_splitter(data)
        with open(pickle_file, "wb") as f:
            pickle.dump(probalities, f)

    return probalities


@timeit
def split_compound(compound, probabilities: dict) -> dict:
    """Split a compound word."""
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
    # Calculate scores for each candidate
    scores = []
    for candidate in candidates:
        score = 1
        split_compound = "$$" + candidate + "__"
        for i in range(2, len(split_compound) - 2):
            pentagram = split_compound[i - 2 : i + 3]
            score *= probabilities.get(pentagram, 0.0)
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
    probabilities = load_probabilities()
    # Split the words
    WORDS = [
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
    for word in WORDS:
        print(word, split_compound(word, probabilities))