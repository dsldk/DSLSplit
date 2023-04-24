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

## Description about the method

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

#### Conclusion

The brute mode implementation is a Danish compound splitter that uses a combination of manually split compounds and presumed compounds from historic Danish dictionaries. The implementation calculates probabilities for all character pentagrams containing known places where a split occurs and assigns probabilities to all possible splitting candidates of an unknown word. Although it has limitations, the brute mode implementation can identify most Danish compound joining elements.

Our internal evaluation on 150 random compounds not appearing in the training data showed the following results: when ignoring errors caused by not identifying the "fuge" (joining) element (i.e., the split is in the correct place), the precision was 0.91 and recall was 0.99. When also considering the "fuge" element, the precision was 0.80 and recall was 0.98. These results are not great, but for the present work we further extended the compound splitting by ... [hvad du nu gjorde helt præcist, Nats!]. This means that the correct split not necessarily has to be the most probable split. When we evaluate our compound splitter while allowing the correct split to just be in one of the first 3 most probable splits, we see a precision of 0.98 and a recall of 0.99, which we believe is adequate for our purpose.