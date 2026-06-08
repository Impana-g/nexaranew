from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

chunks_store = []
index = None


def chunk_text(text, chunk_size=500):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks


def build_vector_store(text):

    global index
    global chunks_store

    chunks_store = chunk_text(text)

    embeddings = model.encode(chunks_store)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(
        np.array(embeddings).astype("float32")
    )


def retrieve(query, k=3):

    global index
    global chunks_store

    if index is None:
        return []

    query_embedding = model.encode([query])

    distances, indices = index.search(
        np.array(query_embedding).astype("float32"),
        k
    )

    results = []

    for idx in indices[0]:
        if idx < len(chunks_store):
            results.append(chunks_store[idx])

    return results