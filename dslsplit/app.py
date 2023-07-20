"""FastAPI service for wordres."""
from os import environ
import pandas as pd
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_simple_security import api_key_router, api_key_security
from pathlib import Path
from starlette.responses import PlainTextResponse

from dslsplit import CONFIG, logger
from dslsplit.brute_split import load_probabilities, split_compound
from dslsplit.train_splitter import train_splitter
from dslsplit.splitter import Splitter2


enable_security = environ.get("ENABLE_SECURITY")
if enable_security is None:
    raise ValueError("ENABLE_SECURITY not set")
enable_security = enable_security.lower() in ("true", "1") and True or False
security_str = (
    "\033[1;32mENABLED\033[0m" if enable_security else "\033[1;31mDISABLED\033[0m"
)
logger.info(f"Security: {security_str}")


title = CONFIG.get("splitter", "title")
description = CONFIG.get("splitter", "description")
# compound_split_probabilities = CONFIG.get("splitter", "prob_file")
current_dir = current_dir = Path(__file__).resolve().parent
word_file_path = str(current_dir / CONFIG.get("splitter", "word_file"))


app = FastAPI(
    title=title,
    description="description",
)

if CONFIG.has_option("webservice", "origin"):
    origins = CONFIG.get("webservice", "origin")
    logger.info(f"Allowed origins: {origins}")
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True)
else:
    logger.info("No CORS restrictions")

logger.info(f"Adding API key security")
app.include_router(api_key_router, prefix="/auth", tags=["_auth"])


@app.get("/health", response_class=PlainTextResponse)
def healthcheck() -> str:
    """Healthcheck, for use in automatic ."""
    return "200"


logger.info(f'Train splitter with "{word_file_path}"')
compound_split_probabilities = train_splitter(word_file_path, "careful", lang="da")
lemmas = pd.read_csv(word_file_path, sep=";", usecols=[0], names=["name"])
lemmas = lemmas.name.drop_duplicates().values

splitter = Splitter2(language="da", lemma_list=list(lemmas)).load_from_filepath(
    compound_split_probabilities
)


brute_probabilities = load_probabilities()


@app.get(
    "/split/{word}",
    response_class=JSONResponse,
    dependencies=[Depends(api_key_security)],
)
async def split(
    word: str, method: str = "mixed", variant: str = "nudansk", lang: str = "da"
) -> JSONResponse:
    """
    Return word split into tokens and scores and scores for each possible split

    Args:
        **word**: word to split into subtokens
        **lang**: language (Only "da" for Danish is supported)
        **method**: "mixed" (default), "careful" or "brute"
        **variant**: "nudansk" (default) or "yngrenydansk"

    Returns:
        Dictionary with keys "word", possible "splits", "description" and "method".
    """
    if method not in ("mixed", "careful", "brute"):
        raise ValueError(f"Method {method} not supported")
    if variant not in ("nudansk", "yngrenydansk"):
        raise ValueError(f"Variant {variant} not supported")
    if lang not in ("da"):
        raise ValueError(f"Language {lang} not supported")

    splits = {}
    if method in ("careful", "mixed"):
        splitter.language = lang
        splits = splitter.easy_split(word)
        splits = [split for split in splits if split["score"] > 0]
        if splits:
            method = "careful"
    if not splits and method not in ("careful",):
        brute_split = split_compound(word, brute_probabilities[variant])
        splits = brute_split.get("splits", [])
        method = "brute"

    message = {
        "word": word,
        "splits": splits,
        "method": method,
        "description": CONFIG.has_option(method, "description")
        and CONFIG.get(method, "description")
        or "",
    }
    return JSONResponse(content=message)


if not enable_security:
    app.dependency_overrides[api_key_security] = lambda: None
