import os
from functools import lru_cache
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / "data" / "hf_home"))
os.environ.setdefault("HF_XET_CACHE", str(PROJECT_ROOT / "data" / "hf_home" / "xet"))

from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-small"
MODEL_CACHE = PROJECT_ROOT / "data" / "models"

@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME, cache_folder=str(MODEL_CACHE))
