# src/rag/indexer.py

import faiss
from sentence_transformers import SentenceTransformer
import pickle
from scraper import SimpleScraper
import asyncio


class RAGIndexer:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.embedder = SentenceTransformer(model_name)

    def chunk(self, text, chunk_size=200):
        words = text.split()
        for i in range(0, len(words), chunk_size):
            yield " ".join(words[i : i + chunk_size])

    def build_faiss(
        self, docs_dict, index_path="faiss_index.bin", meta_path="meta.pkl"
    ):
        chunks = []
        metadata = []

        for url, content in docs_dict.items():
            for chunk in self.chunk(content):
                chunks.append(chunk)
                metadata.append({"source": url, "text": chunk})

        embeddings = self.embedder.encode(chunks, convert_to_numpy=True)
        dimension = embeddings.shape[1]

        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        faiss.write_index(index, index_path)

        with open(meta_path, "wb") as f:
            pickle.dump(metadata, f)

        return index_path, meta_path


if __name__ == "__main__":

    # 1. Example: scrape some URLs (or load your local docs)
    urls = [
        "https://theconceptwardrobe.com/colour-analysis-comprehensive-guides/seasonal-color-analysis-which-color-season-are-you",
        "https://anuschkarees.com/blog/2013/09/24/colour-analysis-part-i-finding-your-type",
        "https://www.diamantipertutti.com/blog/right-jewelry-for-your-skin-tone",
        "https://www.hsamuel.co.uk/blog/what-jewellery-suits-my-skin-tone-an-autumn-colour-palette",
        "https://jasperandelm.com/blogs/news/which-jewelry-looks-best-on-me",
        "https://jewellerybymash.com/blogs/jewellery-giude/what-colour-jewellery-suits-me",
        "https://camillestyles.com/style/fashion/color-analysis/",
    ]
    scraper = SimpleScraper()
    docs = asyncio.run(scraper.scrape(urls))

    # 2. Build FAISS index
    indexer = RAGIndexer()
    index_path, meta_path = indexer.build_faiss(
        docs, index_path="src/rag/faiss_index.bin", meta_path="src/rag/meta.pkl"
    )
    print(f"FAISS index built at {index_path}, metadata at {meta_path}")
