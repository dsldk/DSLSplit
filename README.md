# DSLSplit

CompoundSplitter for Danish

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


## Download

```console
git clone https://github.com/dsldk/lexiscore.git
```

## Security with API keys

Security with API keys can be enabled by setting the environment variable `ENABLE_SECURITY=true`. 

Security uses a DSL fork of fastapi_simple_security: [https://github.com/dsldk/fastapi_simple_security]

Security is not activated by default. The following steps is only relevant if security is enabled.

### Master password

Set master keyword for the Swagger UI with the environment variable `FASTAPI_SIMPLE_SECURITY_SECRET`, e.g.:

`FASTAPI_SIMPLE_SECURITY_SECRET=some_secret_password``

### Adding API keys

When enabled, API keys can be added using the Swagger UI for the webservice (reached on /docs url, see below), or be adding a csv file with the following format:

`
NAME_OF_KEY;API_KEY;EXPIRATION_DATE
`

e.g.:

`test;2d3922ea-c5cc-4d08-8be5-4c71c23c29f1;2023-12-01`

The csv file should be set with the environmental variable `FASTAPI_SIMPLE_SECURITY_API_KEY_FILE`, e.g.:

`FASTAPI_SIMPLE_SECURITY_API_KEY_FILE=/path/to/apikeys.txt`

## Run with Docker

To run the webservice with Docker, a Docker client needs to be installed. See [Docker documentation](https://www.docker.com) for details.

### In development mode

```console
docker compose --env-file dev.env up --build
```

Add "-d" switch to run as daemon.

### In production mode

In production mode security is activated and log level is set to warning.

```console
docker compose --env-file prod.env up --build
```

Add "-d" switch to run as daemon.

### Custom environment file

We provide a default development and production environment file.
This is an example of the production file:

```bash
API_KEYS_FILE=./apikeys.prod.txt
LOG_LEVEL=WARNING
PORT=nnnn
ENABLE_SECURITY=true
```
To create custom development or production modes, simply either change the respective environment files or create a new custom file. 

To run Docker with the custom setup, remember to change the parameter `--env-file``

## Run from terminal

Setup virtual environment:

```console
ACTIVATE ENVIRONMENT
pip install -r requirements.txt
pip install .
```

Run with uvicorn:

```bash
cd lexiscore
uvicorn app:app --PORT nnnn
```

### Optional setup

Set optional setup environment variables before running to activate API key security:

```bash
ENABLE_SECURITY=true
FASTAPI_SIMPLE_SECURITY_SECRET=some_secret_password
FASTAPI_SIMPLE_SECURITY_API_KEY_FILE=/path/to/apikeys.txt
LOG_LEVEL=INFO
```

The webservice should now be accessible on port _nnnn_ with some_secret_password as the master password that can be used to create api-keys to access the actual endpoints from localhost:8000/docs.

## Setup
### Train splitter probabilities
The compound splitter can be trained on custom data.
The training requires a lemma list (not a full form list!)

The training is executed by following command:
```bash
cd lextools
python train_splitter.py -i /path/to/lemma_list.csv -n output_name
```


## Endpoints

See:

* localhost:9002/docs (development)
* localhost:8002/docs (production)

## Accessing the webservice

```python
import requests
from json import loads

URL = "http://localhost:nnnn"
word = "husar"
api_key = "2d3922ea-c5cc-4d08-8be5-4c71c23c29f1"
params = {"lang": "da", "api-key": api_key}

response = requests.get(f"{URL}/check/{word}", params=params)
result = loads(response.text)
# {"word":"husar","valid":true,"score":0.00024243456583721002}

params = {"api-key": api_key}
response = requests.get(f"{URL}/lang/{word}", params=params)
result = loads(response.text)
# [["da",0.00024243456583721002],["de",0.00021127065052605355],["da_lemma",0.0001922643763442915],["en",4.605676657984788e-06]]
```