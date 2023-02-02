"""FastAPI service for wordres."""
import logging
import os

from fastapi import FastAPI
from fastapi_simple_security import api_key_router, api_key_security
from fastapi.responses import PlainTextResponse

# from wordres import CONFIG

logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TITLE = "LexTools"


app = FastAPI(
    title=TITLE,
    description="Lorem ipsum",
)

app.include_router(api_key_router, prefix="/auth", tags=["_auth"])


@app.get("/health", response_class=PlainTextResponse)
def healthcheck() -> str:
    """Healthcheck, for use in automatic ."""
    return "200"


@app.get("/", response_class=PlainTextResponse)
def index() -> str:
    """Return title."""
    return f'{TITLE}: {os.getenv("MODEL_NAME")}'
