"""Evaluation of the DSLSplit webservice."""
import csv
import requests


def main(
    method: str = "brute",
    port: int = 9001,
    size: int | None = None,
    ignore_fuge: bool = True,
    in_top: int = 1,
    print_negatives: bool = False,
) -> None:
    # Load CSS file with evaluation data
    with open("evaluation_data.csv") as f:
        reader = csv.reader(f, delimiter=";")
        data = list(reader)[0:]  # No header row

    # Send requests to FastAPI webservice and compare with expected output
    tp = 0  # True positives
    fp = 0  # False positives
    fn = 0  # False negatives
    tn = 0  # True negatives
    false_positives = []
    false_negatives = []
    for i, (query, expected_output) in enumerate(data):
        params = {"method": method}
        response = requests.get(f"http://localhost:{port}/split/{query}", params=params)
        if response.status_code == 200:
            result = response.json()
            actual_output = result.get("splits", [])
            actual_method = result.get("method", "")
        else:
            actual_output = []
            actual_method = ""

        actual_splits = []
        for split in actual_output[:in_top]:
            if len(split.get("subtokens", [])) > 1:
                actual_splits.append(
                    split["subtokens"][0]
                    + "+"
                    + (split.get("fuge") and split.get("fuge") + "+" or "")
                    + split["subtokens"][1]
                )

        if ignore_fuge:
            new_output = []
            for actual_split in actual_splits:
                actual_split = actual_split.replace("+s+", "s+")
                actual_split = actual_split.replace("+e+", "e+")
                new_output.append(actual_split)
            actual_splits = new_output
            expected_output = expected_output.replace("+s+", "s+")
            expected_output = expected_output.replace("+e+", "e+")

        if actual_splits:
            if expected_output in actual_splits:
                tp += 1
            else:
                fp += 1
                false_positives.append(
                    (query, expected_output, actual_splits, actual_method)
                )
        else:
            if expected_output in actual_splits:
                tn += 1
            else:
                fn += 1
                false_negatives.append(
                    (query, expected_output, actual_splits, actual_method)
                )

        if size and i > size:
            break

    # Calculate precision and recall
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)

    print("===============")
    print(f"Method: {method}")
    print(f"Size: {size}")
    print(f"Top {in_top}")
    print(f"Ignore Fuge: {ignore_fuge}")
    print("---------------")

    if print_negatives:
        # Print results
        print("False positives:")
        for query, expected_output, actual_output, actual_method in false_positives:
            #    if not expected_output:
            #        continue
            print(
                f"Query: {query}, Expected output: {expected_output}, Actual output: {actual_output} (method: {actual_method}))"
            )
        print("False negatives:")
        for query, expected_output, actual_output, actual_method in false_negatives:
            print(
                f"Query: {query}, Expected output: {expected_output}, Actual output: {actual_output} (method: {actual_method})))"
            )

    print(f"True positives: {tp}")
    print(f"True negatives: {tn}")
    print(f"Total: {tp + tn + fp + fn}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")


if __name__ == "__main__":
    main(method="careful", size=150, ignore_fuge=False, in_top=1)
    main(method="careful", size=150, ignore_fuge=True, in_top=1)
    main(method="careful", size=150, ignore_fuge=False, in_top=3)
    main(method="careful", size=150, ignore_fuge=True, in_top=3)

    main(method="brute", size=150, ignore_fuge=False, in_top=1)
    main(method="brute", size=150, ignore_fuge=True, in_top=1)
    main(method="brute", size=150, ignore_fuge=False, in_top=3)
    main(method="brute", size=150, ignore_fuge=True, in_top=3)

    main(method="mixed", size=150, ignore_fuge=False, in_top=1)
    main(method="mixed", size=150, ignore_fuge=True, in_top=1)
    main(method="mixed", size=150, ignore_fuge=False, in_top=3)
    main(method="mixed", size=150, ignore_fuge=True, in_top=3)
