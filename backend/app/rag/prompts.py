"""Prompt construction for grounded question answering.

Kept separate from the LLM transport (``llm.py``) so prompts can be iterated
without touching API code, and so prompt building is unit-testable on its own.
"""

from dataclasses import dataclass

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about a company's "
    "internal documents. Answer the user's question using ONLY the provided "
    "context. If the context does not contain the answer, say you don't have "
    "enough information from the documents to answer — do not invent facts. "
    "Cite the source document name(s) you used. Be concise and accurate."
)


@dataclass(frozen=True)
class ContextItem:
    """A single piece of retrieved context to ground the answer."""

    source: str  # human-readable label, e.g. "handbook.pdf (chunk 2)"
    text: str


def build_user_prompt(question: str, contexts: list[ContextItem]) -> str:
    """Assemble the user message: numbered context blocks + the question."""
    if contexts:
        blocks = [
            f"[Source {i}: {c.source}]\n{c.text}"
            for i, c in enumerate(contexts, start=1)
        ]
        context_str = "\n\n".join(blocks)
    else:
        context_str = "(no relevant context found)"

    return (
        "Context:\n"
        f"{context_str}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )
