"""
Embedder using Sentence Transformers.
Singleton pattern so the model is loaded once per process.
"""
from __future__ import annotations
import logging
from functools import lru_cache
from typing import Union

logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model: {model_name}")
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(model_name)
        self._model_name = model_name
        logger.info("Embedding model loaded")

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed(self, texts: Union[str, list[str]]) -> list[list[float]]:
        """Embed one or more texts. Always returns a list of float vectors."""
        if isinstance(texts, str):
            texts = [texts]
        vectors = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return vectors.tolist()

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


@lru_cache(maxsize=1)
def get_embedder(model_name: str = "all-MiniLM-L6-v2") -> Embedder:
    return Embedder(model_name)
