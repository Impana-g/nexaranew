from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from anthropic import Anthropic
from core.config import ANTHROPIC_API_KEY

print("ANTHROPIC KEY FOUND:", bool(ANTHROPIC_API_KEY))
print("KEY LENGTH:", len(ANTHROPIC_API_KEY))

client = Anthropic(
    api_key=ANTHROPIC_API_KEY
)

model = SentenceTransformer("all-MiniLM-L6-v2")

chunks_store = []
index = None


def chunk_text(text, chunk_size=1500):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks


def build_vector_store(text):

    global index
    global chunks_store

    chunks_store = chunk_text(text)

    print("Total Chunks:", len(chunks_store))

    embeddings = model.encode(
        chunks_store,
        batch_size=32,
        show_progress_bar=True
    )

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


def generate_answer(question, chunks):

    try:

        context = "\n\n".join(chunks)

        prompt = f"""
You are a financial document analyst.

Use ONLY the provided context.

Context:
{context}

Question:
{question}

Answer clearly and concisely.
"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.content[0].text

    except Exception as e:
        return f"CLAUDE ERROR: {str(e)}"


def analyze_financial_document(text):

    try:

        prompt = f"""
You are a senior investment analyst.

Analyze the following annual report and provide a professional investment recommendation.

Financial Report:
{text[:10000]}

Return the response in this format:

Recommendation: BUY / HOLD / AVOID

Risk Level: LOW / MEDIUM / HIGH

Key Strengths:
- Point 1
- Point 2
- Point 3

Key Risks:
- Point 1
- Point 2

Investment Summary:
(2-3 sentences)
"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.content[0].text

    except Exception as e:
        return f"CLAUDE ERROR: {str(e)}"