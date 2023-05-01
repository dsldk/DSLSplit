# DSLSplit

CompoundSplitter for Danish

## Download

```bash
git clone https://github.com/dsldk/dslsplit
```

## Setup

DSLSplit needs some files to run. Three files are needed. Use either

```bash
git secret reveal
```

to unpack the .secret versions of the files from the repository. Or create empty versions of them:

```bash
touch apikeys.prod.txt
touch apikeys.dev.txt
touch secrets.env
```

## Run in Docker

```bash
docker compose --env-file=dev.env up --build
OR
docker compose --env-file=prod.env up --build
```

The webservice will now be accessible on localhost:9001  or localhost:8001 (production). Ports can be changed in the prod.env and dev.env files. Add "-d" for detached mode.

## Run from terminal (without Docker)

Setup virual environment:

```bash
ACTIVATE ENVIRONMENT
pip install -r requirements.txt
pip install .
```

Setup environment variables:

```bash
export LOG_LEVEL=INFO
export ENABLE_SECURITY=false
```

Run:

```bash
cd dslsplit
uvicorn app:app --PORT 8000
```

The webservice should now be accessible on port 8000

## API Key security

Enable api key security with

```bash
export ENABLE_SECURITY=true
```

Supply the master keyword for Fastapi_simple_security in the `secrets.env` file:

```env
FASTAPI_SIMPLE_SECURITY_SECRET=some_secret_password
```

Use this password to create api-keys from the web interface if security is enabled:

```url
http://localhost:9001/docs
```

List any known api-keys in the apikeys..txt files with format:

```csv
NAME_OF_KEY;API_KEY;EXPIRATION_DATE
```

e.g.:

```csv:
test;2d3922ea-c5cc-4d08-8be5-4c71c23c29f1;2023-12-01
```


## Using the modules

### Train splitter probabilities

```bash
cd lextools
python train_splitter.py -i /path/to/uniq_lemma_ddo.csv -n da_test
```

## About the method

It is possible to split a word in three modes:

* careful: Using an adaption version of ...
* brute: Using a probabilities from known compounds from Den Danske Ordbog (see below). This mode do not reliably identify the joining elements between to two parts of the compound ("s" and "e")
* mixed: first attempting a split using the careful mode, and if this fails, the brut mode

### Brute mode

The brute mode is suitable for identifying Danish compound joining elements except "e" and "s". This implementation uses a combination of 30,211 manually split compounds from [_Den Danske Ordbog_](ordnet.dk/ddo) and 165,475 presumed compounds from the historic Danish dictionary [_Ordbog over det danske Sprog_](ordnet.dk/ods) covering the Danish language from 1700-1950. These word added when it became clear that the manually split compounds not were sufficient data.

#### Methodology

The brute splitter implementation first calculates probabilities for all character pentagrams containing known places where a split occurs. For instance, the Danish word "vegatarburger" is split like "vegetar+burger" resulting in the following pentagrams: "etar+", "tar+b", "ar+bu", "r+bur", and "+burg". To account for any compound splits early and late in the words, we prefix the word with "$$" and suffix the word with "__". The probability is calculated as the number of times a particular pentagram occurs divided by the total number of pentagrams.

To split an unknown word using the brute method, we first list all the possible places where a split may occur. For instance, the word "havesaks" ("garden scissors") has seven split candidates: "h+avesaks," "ha+vesaks," "hav+esaks," "have+saks," "haves+aks," "havesa+ks," and "havesak+s." We add the productive joining elements for Danish compounds, "e" and "s," to the candidates as well: "hav+e+saks" and "have+s+aks."

For each splitting candidate, we calculate the probability, assigning a low probability to any unknown pentagrams (specifically 1e-10) and a very low probability to any unknown pentagrams including the prefix ($) or suffix (_) characters to penalize splitting very early and late in the word. To the basic score, we slightly penalize splits the longer they occur from the center of the word.

#### Limitations

The brute mode is not ideal for identifying the Danish compound joining elements, "e" and "s", due to the quality of the data used from the historic Danish dictionary.

#### Self-evaluation

By running the evaluation.py script the _careful_, _brute_, and _mixed_ modes are evaluation against 152 random compounds not included in the training data, with and without disregarding the joining element.

#### Conclusion

The brute mode implementation is a Danish compound splitter that uses a combination of manually split compounds and presumed compounds from historic Danish dictionaries. The implementation calculates probabilities for all character pentagrams containing known places where a split occurs and assigns probabilities to all possible splitting candidates of an unknown word. Although it has limitations, the brute mode implementation can identify most Danish compound joining elements.
