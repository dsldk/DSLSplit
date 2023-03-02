"""FastAPI service for wordres."""
import logging
from fastapi import FastAPI
from fastapi_simple_security import api_key_router
from fastapi.responses import JSONResponse
from starlette.responses import PlainTextResponse

from lextools import CONFIG
from lextools.easy_split import load_probabilities, split_compound

# from splitter import Splitter2

logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


title = CONFIG.get("splitter", "title")
description = CONFIG.get("splitter", "description")
compound_split_probabilities = CONFIG.get("splitter", "prob_file")
word_file_path = CONFIG.get("splitter", "word_file")

app = FastAPI(
    title=title,
    description="description",
)

app.include_router(api_key_router, prefix="/auth", tags=["_auth"])


@app.get("/health", response_class=PlainTextResponse)
def healthcheck() -> str:
    """Healthcheck, for use in automatic ."""
    return "200"


# lemmas = pd.read_csv(word_file_path, sep=";", usecols=[0], names=['name'])
# lemmas = lemmas.name.drop_duplicates().values

# splitter = Splitter2(language="da", lemma_list=lemmas).load_from_filepath(compound_split_probabilities)


# @app.get("/split/{word}", response_class=JSONResponse)
# def split(word: str, lang: str = "da", period: str | None = None) -> JSONResponse:
#     """
#     Return word split into tokens and scores and scores for each possible split

#     - **word**: word to split into subtokens
#     - **lang**: language ("da" for Danish or "de" for german)
#     - **period**: for future functionality
#     """
#     splitter.language = lang
#     splits = splitter.easy_split(word)
#     return JSONResponse(content={"word": word, "splits": splits})

probabilities = load_probabilities()


@app.get("/split/{word}", response_class=JSONResponse)
def split(word: str) -> JSONResponse:
    """
    Return word split into tokens and scores and scores for each possible split

    - **word**: word to split into subtokens

    """
    splits = split_compound(word, probabilities)
    return JSONResponse(content=splits)
