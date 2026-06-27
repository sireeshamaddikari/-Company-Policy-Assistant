"""Text splitting using LangChain's RecursiveCharacterTextSplitter.

Thin wrapper so the rest of the app depends on a small ``split`` interface and
the chunk size/overlap are driven by configuration.
"""

import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class TextSplitter:
    """Splits raw document text into overlapping chunks."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def split(self, text: str) -> list[str]:
        """Return non-empty chunks for the given text."""
        chunks = [c for c in self._splitter.split_text(text) if c.strip()]
        logger.debug("Split text into %d chunks", len(chunks))
        return chunks
