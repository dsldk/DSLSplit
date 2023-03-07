# lextools

CompoundSplitter for Danish

## Download

```bash
git clone https://github.com/dsldk/lextools
```

## Install dependencies

```bash
[ACTIVATE VIRTUAL INVORENMENT]
pip install -r requirements.txt
pip install -e .
```

## Run in development mode

```bash
cd lextools
uvicorn app:app --reload
```

## Run a Docker container

```bash
docker compose up -d
```

## Using the modules

### Train splitter probabilities

```bash
cd lextools
python train_splitter.py -i /path/to/uniq_lemma_ddo.csv -n da_test
```
