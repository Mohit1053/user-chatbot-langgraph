import os
import csv
import io
import requests
from typing import List, Dict, Optional

from sentence_transformers import SentenceTransformer
from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone

# === Constants ===
FIREBASE_FAQ_CSV_URL = os.getenv("FIREBASE_FAQ_CSV_URL")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

INDEX_NAME = "faq-index"  # Make sure this index exists in Pinecone
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 outputs 384-d embeddings
THRESHOLD = 0.35  # max cosine distance


# === Embedding Model ===
model = SentenceTransformer("all-MiniLM-L6-v2")

# === Pinecone Setup ===
pc = Pinecone(api_key=PINECONE_API_KEY)

# === Load FAQ CSV ===
def load_faq_csv() -> List[Dict]:

    response = requests.get(FIREBASE_FAQ_CSV_URL)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch FAQ CSV. Status: {response.status_code}")

    csv_buffer = io.StringIO(response.text)
    reader = csv.DictReader(csv_buffer)

    faq_data = []
    for row in reader:
        faq_data.append({
            "id": row["id"],
            "question": row["question"],
            "answer": row["answer"],
            "type": row.get("type", "single")
        })
    
    csv_buffer.close()
    return faq_data


# Connect to existing index or error if not created
if not pc.has_index(INDEX_NAME):
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ),
        tags={
            "environment": "development"
        }
    )
index = pc.Index(INDEX_NAME)

# === Upload FAQs if index is empty ===
def initialize_index_if_empty():

    stats = index.describe_index_stats()
    if stats["total_vector_count"] == 0:
        faq_rows = load_faq_csv()
        print("Index empty. Uploading FAQ embeddings...")

        vectors = []
        for faq in faq_rows:
            vector = model.encode(faq["question"]).tolist()
            vectors.append((
                faq["id"],  # vector id
                vector,     # embedding
                {           # metadata
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "type": faq["type"]
                }
            ))
        index.upsert(vectors)
        print(f"Uploaded {len(vectors)} FAQs to Pinecone.")

initialize_index_if_empty()

# === Search Function ===
def match_faq(user_query: str, k: int = 1, max_distance: float = THRESHOLD) -> Optional[Dict]:
    query_vec = model.encode(user_query).tolist()

    result = index.query(
        vector=query_vec,
        top_k=k,
        include_metadata=True
    )

    matches = result.get("matches", [])

    if not matches:
        return None

    best_match = matches[0]
    score = best_match["score"]
    distance = 1 - score  # Convert similarity to distance

    if distance > max_distance:
        return None

    metadata = best_match["metadata"]
    return {
        "id": best_match.id,
        "question": metadata["question"],
        "answer": metadata["answer"],
        "type": metadata["type"],
        "score": score
    }
