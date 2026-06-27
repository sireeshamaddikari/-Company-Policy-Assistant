"""Citation model (stub).

Links an assistant message to the document chunk(s) it was grounded on, so the
UI can show "sources" for each answer.

Planned columns:
    id           : primary key
    message_id   : FK -> messages.id
    document_id  : FK -> documents.id
    chunk_index  : which chunk within the document
    snippet      : the quoted text shown to the user
    score        : retrieval similarity score
"""
