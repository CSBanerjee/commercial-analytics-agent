import json
from pathlib import Path
import numpy as np

from llm_client import LLMClient


class RAGRetriever:

    def __init__(self):
        self.llm = LLMClient()

        self.chunks_path = Path(__file__).parent / "rag_chunks.json"

        with open(self.chunks_path, "r", encoding="utf-8") as file:
            self.chunks = json.load(file)

        self.embeddings = self._create_embeddings(
            [chunk["content"] for chunk in self.chunks]
        )

    def _create_embeddings(self, texts):

        response = self.llm.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )

        return np.array([
            item.embedding for item in response.data
        ])

    def retrieve(self, question, top_k=2):

        question_embedding = self._create_embeddings([question])[0]

        similarities = np.dot(
            self.embeddings, question_embedding
        ) / (
            np.linalg.norm(self.embeddings, axis=1)
            * np.linalg.norm(question_embedding)
        )

        top_indices = np.argsort(similarities)[::-1][:top_k]

        retrieved_chunks = [
            self.chunks[index]["content"]
            for index in top_indices
        ]

        return "\n\n".join(retrieved_chunks)