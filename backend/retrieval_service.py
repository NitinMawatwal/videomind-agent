import faiss
import numpy as np

from backend.embedding_service import embed_texts


class RetrievalService:
    def __init__(self):
        self.index = None
        self.chunks = []

    def add_chunks(self, chunks: list[dict]) -> None:
        if not chunks:
            return

        texts = [chunk["text"] for chunk in chunks]
        vectors = np.asarray(
            embed_texts(texts),
            dtype="float32",
        )

        faiss.normalize_L2(vectors)

        if self.index is None:
            self.index = faiss.IndexFlatIP(vectors.shape[1])

        self.index.add(vectors)
        self.chunks.extend(chunks)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if self.index is None or not self.chunks:
            return []

        query_vector = np.asarray(
            embed_texts([query]),
            dtype="float32",
        )

        faiss.normalize_L2(query_vector)

        k = min(top_k, len(self.chunks))
        scores, indices = self.index.search(query_vector, k)

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue

            result = self.chunks[index].copy()
            result["score"] = float(score)
            results.append(result)

        return results

retrieval_service = RetrievalService()