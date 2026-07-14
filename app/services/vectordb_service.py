import asyncio
import json
from typing import List, Dict, Any, Optional
import time
from pinecone import Pinecone, ServerlessSpec
# from sentence_transformers import SentenceTransformer
from app.config import config
from app.services.youtube_fetch import YouTubeService

from google import genai


class VectorDB:

    def __init__(
        self,
        api_key: str = config.PINECONE_API_KEY,
        index_name: str = config.PINECONE_INDEX_NAME,
        dimension: int = config.PINECONE_DIMENSION,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1",
        ):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric

        self._create_index_if_not_exists(cloud, region)
        self.index = self.pc.Index(index_name)
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)

    # -----------------------------
    # Index Methods
    # -----------------------------

    def _create_index_if_not_exists(self, cloud, region):
        indexes = [idx["name"] for idx in self.pc.list_indexes()]

        if self.index_name not in indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                    cloud=cloud,
                    region=region,
                ),
            )

    def delete_index(self):
        self.pc.delete_index(self.index_name)

    # -----------------------------
    # Upsert
    # -----------------------------

    def upsert(
        self,
        id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
    ):
        self.index.upsert(
            vectors=[
                {
                    "id": id,
                    "values": embedding,
                    "metadata": metadata,
                }
            ]
        )

    def upsert_batch(self, vectors: List[Dict]):
        return bool(self.index.upsert(vectors=vectors))

    # async def encode(self, text: str) -> list[float]:
    #     """
    #     Generate embedding for a single text.
    #     """
    #     model = SentenceTransformer(config.EMBEDDING_MODEL)

    #     embedding = model.encode(
    #         text,
    #         normalize_embeddings=True
    #     )

        # return embedding.tolist()
    
    def encode(self, text: str) -> list[float]:
        result = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
        )
        return result.embeddings[0].values


    def to_upsert_vectors(self, videos: List[Dict], embeddings: List[List[float]], source: str) -> List[Dict]:
        """
        Convert videos and embeddings into Pinecone upsert format.
        source: "youtube" or "github"
        """
        vectors = []

        for video, embedding in zip(videos, embeddings):
            vectors.append({
                "id": video["id"],
                "values": embedding,
                "metadata": {
                    "title": video["title"],
                    "description": video["description"],
                    "url": video["url"],
                    "source": source,
                }
            })

        return vectors
    
    def ingest(self, items: List[Dict], source: str) -> bool:
        """
        Embed and upsert a batch of items, tagged with their source.
        Each item must have: id, title, description, url
        """
        embeddings = []
        for item in items:
            text = f"Title: {item['title']}\n\nDescription:\n{item['description']}"
            embedding = self.encode(text)
            embeddings.append(embedding)

        vectors = self.to_upsert_vectors(items, embeddings, source=source)
        return self.upsert_batch(vectors)

    # -----------------------------
    # Search
    # -----------------------------

    async def search(
        self,
        embedding: List[float],
        top_k: int = 5,
        include_metadata: bool = True,
    ):
        return self.index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=include_metadata,
        )

    # -----------------------------
    # Fetch
    # -----------------------------

    def fetch(self, ids: List[str]):
        return self.index.fetch(ids=ids)

    # -----------------------------
    # Delete
    # -----------------------------

    def delete(self, ids: List[str]):
        self.index.delete(ids=ids)

    def delete_all(self):
        self.index.delete(delete_all=True)

    # -----------------------------
    # Update Metadata
    # -----------------------------

    def update(
        self,
        id: str,
        metadata: Dict[str, Any],
    ):
        self.index.update(
            id=id,
            set_metadata=metadata,
        )

    # -----------------------------
    # Stats
    # -----------------------------

    def describe(self):
        return self.index.describe_index_stats()

    # -----------------------------
    # Rerank
    # -----------------------------

    async def rerank(
        self,
        query: str,
        documents: List[Dict],
        model: str = "bge-reranker-v2-m3",
        top_n: int = 5,
    ):
        return self.pc.inference.rerank(
            model=model,
            query=query,
            documents=documents,
            rank_fields=["text"],
            top_n=top_n,
        )
    
if __name__ == "__main__":
    youtube_s = YouTubeService()
    videos = youtube_s.get_channel_videos()
    with open("videos.json", "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=4)
    print("Video content fetched.....")
    vectordb = VectorDB()
    embeddings = []
    for v in videos:
        text = f"Title: {v['title']}\n\nDescription:\n{v['description']}"
        embedding = vectordb.encode(text)
        embeddings.append(embedding)
        time.sleep(1)
    print("Embedding generated .....")
    vectors = vectordb.to_upsert_vectors(videos, embeddings)
    with open("vectors.json", "w", encoding="utf-8") as f:
        json.dump(vectors, f, indent=4)
    print("Vectors created.....")
    upsert = vectordb.upsert_batch(vectors)
    print("Upsert condition :", upsert)
    

    # print(vectordb._create_index_if_not_exists())