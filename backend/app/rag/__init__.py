"""RAG infrastructure package.

Holds the retrieval-augmented-generation building blocks behind interfaces
(see ``interfaces.py``): an embedder, a vector store, and an LLM client. Coding
the rest of the app against these Protocols means FAISS can be swapped for
pgvector, or Mistral for another provider, by changing a single wiring point
rather than rewriting services.
"""
