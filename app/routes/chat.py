from fastapi import APIRouter
from pydantic import BaseModel

from app.config import config
from app.services.vectordb_service import VectorDB

router = APIRouter(prefix="/api", tags=["Chat"])
vectordb = VectorDB()


class ChatRequest(BaseModel):
    query: str


@router.post("/chat")
async def chat(request: ChatRequest):

    # Generate query embedding
    query_embedding = vectordb.encode(request.query)

    # Search Pinecone
    search_results = vectordb.search(
        embedding=query_embedding,
        top_k=10,
    )

    # Prepare documents for reranking
    documents = [
        {
            "text": f"""
            Title:
            {match["metadata"]["title"]}

            Description:
            {match["metadata"]["description"]}
            """,
            "metadata": match["metadata"],
        }
        for match in search_results["matches"]
    ]

    # Rerank
    reranked = vectordb.rerank(
        query=request.query,
        documents=documents,
        top_n=3,
    )

    return {
        "query": request.query,
        "results": [
         {
            "index": r.index,
            "score": r.score,
            "document": r.document,
        }
        for r in reranked.data
        ],
    }