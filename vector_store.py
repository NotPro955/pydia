"""
Phase 2: Embed chunks and store in ChromaDB.
Phase 3: Retrieve top-K sales-relevant chunks.
"""

import chromadb
from chromadb.utils import embedding_functions


# Sales-oriented retrieval queries
SALES_QUERIES = [
    "exceptional talent achievements awards recognition",
    "career highlights milestones breakthrough success",
    "unique skills expertise mastery innovation",
    "influence impact legacy cultural significance",
    "personal qualities character determination resilience",
]


def build_vector_store(person_name: str, chunks: list[dict]) -> chromadb.Collection:
    """Embed all chunks and store them in an in-memory ChromaDB collection."""
    client = chromadb.Client()  # In-memory (no persistence needed per session)

    # Use a lightweight but strong sentence-transformer model
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Collection name: sanitize person name
    col_name = "".join(c if c.isalnum() else "_" for c in person_name)[:50]

    # Delete collection if exists (fresh run)
    try:
        client.delete_collection(col_name)
    except Exception:
        pass

    collection = client.create_collection(name=col_name, embedding_function=ef)

    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [{"section": c["section"]} for c in chunks]

    # ChromaDB has a max batch size — split if large
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        collection.add(
            documents=texts[i : i + batch_size],
            ids=ids[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )

    print(f"[VectorDB] Stored {collection.count()} chunks for '{person_name}'")
    return collection


def retrieve_sales_context(collection: chromadb.Collection, top_k: int = 5) -> str:
    """
    Run multiple sales-oriented queries against the collection,
    deduplicate results, and return a single context string.
    """
    seen_ids = set()
    results = []

    for query in SALES_QUERIES:
        resp = collection.query(query_texts=[query], n_results=top_k)
        docs = resp["documents"][0]
        ids = resp["ids"][0]
        for doc, doc_id in zip(docs, ids):
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                results.append(doc)

    context = "\n\n".join(results)
    print(f"[Retriever] Retrieved {len(results)} unique chunks as context")
    return context
