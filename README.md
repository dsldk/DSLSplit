# lextools
Misc. tools for NLP based on DLS's resources

## Installation

1. Activate a virtual environment with python3.11

2. 

```
git clone https://github.com/dsldk/lextools
pip install -r requirements.txt
pip install -e .
```

## Train probabilities

This step can be skipped when using easy_split.

```
cd lextools
python train_splitter.py -i /path/to/uniq_lemma_ddo.csv -n da_test

```

## Start webservice in development mode

```
uvicorn app:app --reload


