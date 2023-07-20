import json
import re
from charsplit.splitter import ngram_probs as de_ngram_probs
from typing import List, Tuple, Dict


class Splitter2:
    """Customised version of German compound splitter developed by Don Tuggener.
    Original code can be found at: https://github.com/dtuggener/CharSplit
    """

    def __init__(
        self,
        ngram_probs: dict = de_ngram_probs,
        language: str = "de",
        lemma_list: List | None = None,
    ):
        self.ngram_probs = ngram_probs
        self.language = language
        self.lemma_list = lemma_list

    def split_compound(self, word: str) -> List[Tuple[float, str, str]]:
        """Return list of possible splits, best first.

        Args:
            word: Word to be split

        Returns:
            List of all splits
        """

        def cut_fuge(word_slice: str, language: str) -> tuple:
            min_len = 3
            end_slices = ["s"]
            if language == "de":
                end_slices = ["ts", "gs", "ks", "hls", "ns"]

            elif language == "da":
                end_slices = [
                    "teks",
                    "ions",
                    "ngs",
                    "ms",
                    "ns",
                    "ds",
                    "bs",
                    "vs",
                    "ls",
                    "rs",
                    "js",
                ]

            if len(word_slice) >= min_len + 1:
                if any([word_slice.endswith(end_slice) for end_slice in end_slices]):
                    return word_slice[:-1], word_slice[-1]

            return word_slice, ""

        word = word.lower()

        # If there is a hyphen in the word, return part of the word behind the last hyphen
        match = re.search("(.*)-", word)
        if match:
            return [
                (
                    1.0,
                    match.group(1),
                    re.sub(".*-", "", word.title()),
                )
            ]

        scores = list()  # Score for each possible split position

        # Iterate through characters, start at third character, go to 3rd last
        for n in range(2, len(word) - 2):
            pre_slice = word[:n]

            # Cut of Fugen-S
            pre_slice, fuge = cut_fuge(pre_slice, self.language)

            # Start, in, and end probabilities
            pre_slice_prob = list()
            in_slice_prob = list()
            start_slice_prob = list()

            # Extract all ngrams
            for k in range(len(word) + 1, 2, -1):
                # Probability of first compound, given by its ending prob
                if not pre_slice_prob and k <= len(pre_slice):
                    # The line above deviates from the description in the thesis;
                    # it only considers word[:n] as the pre_slice.
                    # This improves accuracy on GermEval and increases speed.
                    # Use the line below to replicate the original implementation:
                    # if k <= len(pre_slice):
                    end_ngram = pre_slice[-k:]  # Look backwards
                    pre_slice_prob.append(
                        self.ngram_probs["suffix"].get(end_ngram, -1)
                    )  # Punish unlikely pre_slice end_ngram

                # Probability of ngram in word, if high, split unlikely
                in_ngram = word[n : n + k]
                in_slice_prob.append(
                    self.ngram_probs["infix"].get(in_ngram, 1)
                )  # Favor ngrams not occurring within words

                # Probability of word starting
                # The condition below deviates from the description in the thesis (see above comments);
                # Remove the condition to restore the original implementation.
                if not start_slice_prob:
                    ngram = word[n : n + k]
                    # Cut Fugen-S
                    ngram, fuge2 = cut_fuge(ngram, language=self.language)

                    start_slice_prob.append(self.ngram_probs["prefix"].get(ngram, -1))

            if not pre_slice_prob or not start_slice_prob:
                continue

            start_slice_prob = max(start_slice_prob)
            pre_slice_prob = max(pre_slice_prob)  # Highest, best pre_slice
            in_slice_prob = min(
                in_slice_prob
            )  # Lowest, punish splitting of good in_grams
            score = start_slice_prob - in_slice_prob + pre_slice_prob
            scores.append((score, word[:n], word[n:], fuge))

        scores.sort(reverse=True)

        if not scores:
            scores = [[0, word, word]]

        return sorted(scores, reverse=True)

    def load_from_filepath(self, filepath):
        """Load a splitter for compound words.

        Args:
            filepath: Path to file with ngram probabilities.

        Returns:
            Splitter probablities."""
        with open(filepath) as f:
            ngram_probs = json.load(f)

        self.ngram_probs = ngram_probs

        return self

    def easy_split(self, word: str, min_score: float = -0.2) -> list:
        """Split compound into words.

        Args:
            word: Word to be split
            min_score: Minimum score for a split to be returned

        Returns:
            List of all splits
        """
        if not self.lemma_list:
            raise ValueError("Lemma list must be set before splitting")
        splits = self.split_compound(word)
        # Lower() because charsplit is developed for German nouns
        output = [(score, split) for score, *split in splits if score > min_score]

        verified = []
        for score, item in output:
            ver_items = {}

            ver_items["fuge"] = item[-1]
            split = item[:-1]

            for part in split:
                if (
                    part[-1] == "s"
                    and part not in self.lemma_list
                    and part[:-1] in self.lemma_list
                ):
                    ver_items["subtokens"].append(part[:-1])
                    ver_items["fuge"] = "s"
                elif (
                    part[-1] == "e"
                    and part not in self.lemma_list
                    and part[:-1] in self.lemma_list
                ):
                    ver_items["subtokens"].append(part[:-1])
                    ver_items["fuge"] = "e"
                else:
                    ver_items["subtokens"].append(part)

            ver_items["score"] = score
            verified.append(ver_items)

        return (
            verified
            if len(verified)
            else [{"subtokens": [word], "score": -1, "fuge": ""}]
        )
