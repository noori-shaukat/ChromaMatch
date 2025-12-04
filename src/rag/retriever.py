# src/rag/retriever.py

import faiss
import pickle
from sentence_transformers import SentenceTransformer


class RAGRetriever:
    def __init__(
        self, index_path="src/rag/faiss_index.bin", meta_path="src/rag/meta.pkl"
    ):
        self.index = faiss.read_index(index_path)
        self.meta = pickle.load(open(meta_path, "rb"))
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def search(self, query, k=5):
        q_emb = self.embedder.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(q_emb, k)

        results = []
        for idx in indices[0]:
            results.append(self.meta[idx])

        return results
