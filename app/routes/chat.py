from fastapi import APIRouter
from pydantic import BaseModel
import httpx
from markdownify import markdownify

from app.config import config
from app.services.vectordb_service import VectorDB
from app.services.prompt_manager import SYSTEM_PROMPT

router = APIRouter(prefix="/api", tags=["Chat"])
vectordb = VectorDB()

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma3:270m"


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    response: str


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

    context = ""

    for i, doc in enumerate(reranked.data, start=1):
        context += f"""
    Document {i}

    Title:
    {doc.document['metadata']['title']}

    Description:
    {doc.document['metadata']['description']}

    ----------------------
    """
    

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content" : SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": context
            }
        ],
        "stream": False
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(OLLAMA_URL, json=payload)

    data = r.json()
    print(data)

    return ChatResponse(
        response=markdownify(data["message"]["content"])
    )