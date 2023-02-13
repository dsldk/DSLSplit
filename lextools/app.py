"""FastAPI service for wordres."""
import logging
import pandas as pd
from fastapi import FastAPI, status
from fastapi_simple_security import api_key_router, api_key_security
from fastapi.responses import JSONResponse

# from wordres import CONFIG
from splitter import Splitter2

logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s",
                    level=logging.INFO
                    )

logger = logging.getLogger(__name__)

TITLE = "LexTools"

app = FastAPI(title=TITLE,
              description="Lorem ipsum",
              )

app.include_router(api_key_router, prefix="/auth", tags=["_auth"])

# todo skal ikke hardkodes her
compound_split_probabilities = "data/da_ngram_probs.json"
lemmas = pd.read_csv("data/lemmaliste_ddo.csv", sep=";", usecols=[0], names=['name'])
lemmas = lemmas.name.drop_duplicates().values

splitter = Splitter2(language="da", lemma_list=lemmas).load_from_filepath(compound_split_probabilities)


@app.get("/split/{lemma}", response_class=JSONResponse)
def split(lemma: str, lang: str = "da", period: str | None = None) -> JSONResponse:
    splitter.language = lang
    splits, scores = splitter.easy_split(lemma)
    return JSONResponse(content={"lemma": lemma, "subtokens": splits, "scores": scores})
