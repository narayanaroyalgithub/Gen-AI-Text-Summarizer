from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class EmbeddingIndex:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.texts = []

    def build(self, texts):
        # texts: list of strings (chunks)
        self.texts = texts
        embs = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        dim = embs.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embs)
        self.embs = embs

    def query(self, query_text, top_k=2):
        q = self.model.encode([query_text], convert_to_numpy=True)
        D, I = self.index.search(q, top_k)
        return [(self.texts[i], float(D[0][j])) for j, i in enumerate(I[0])]
