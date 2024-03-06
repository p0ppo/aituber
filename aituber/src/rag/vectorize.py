import os
import shutil
import warnings

import dotenv
import click
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from .scraper import get_scraper, scraper_alias

dotenv.load_dotenv()

database_list = [
    "all",
    "ff14",
]

embedding_list = [
    "ada_002",
    "multilingual_e5"
]

def _vectorize(database, use_cache):
    scraper = get_scraper(database)()
    docs = scraper.scrape()

    model_name = os.environ.get("VECTOR_STORE_EMBEDDING")
    if model_name not in embedding_list:
        raise ValueError(f"Model name {model_name} is not supported.")
    if model_name == "ada_002":
        embeddings = OpenAIEmbeddings()
    elif model_name == "multilingual_e5":
        embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")

    persist_directory = os.path.join(
        os.environ.get("VECTOR_STORE_PATH"),
        database
    )
    if use_cache:
        if os.path.exists(persist_directory):
            warnings.warn(f"Database: '{persist_directory}' already exists. If you want to clear the cache, set '--use_cache=False'.")
            warnings.warn("Cache is used.")
    else:
        if os.path.exists(persist_directory):
            shutil.rmtree(persist_directory)
        
    db = Chroma.from_texts(
        sum(docs, []),
        embeddings,
        persist_directory=persist_directory,
        )
    db.persist()

@click.command(name="vectorize")
@click.argument("database")
@click.option('--use_cache', default=True)
def vectorize(database, use_cache):
    if database == "all":
        for d in scraper_alias.keys():
            _vectorize(d, use_cache)
    else:
        _vectorize(database, use_cache)