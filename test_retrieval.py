import faiss
import pickle
from sentence_transformers import SentenceTransformer

# Load FAISS index and metadata
index = faiss.read_index("adgm_faiss.index")
with open("adgm_metadata.pkl", "rb") as f:
    data = pickle.load(f)

docs = data["docs"]
metadata = data["metadata"]

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Example query
query = "What are the requirements for Articles of Association in ADGM?"
query_vector = model.encode([query])

# Search
k = 3
distances, indices = index.search(query_vector, k)

print("\nTop Matches:\n")
for idx, dist in zip(indices[0], distances[0]):
    print(f"Source: {metadata[idx]['source']} | Score: {dist:.2f}")
    print(docs[idx][:300] + "...")
    print("-"*50)

