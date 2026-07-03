from fastapi import APIRouter
from pydantic import BaseModel
import httpx
from markdownify import markdownify

from app.config import config
from app.services.vectordb_service import VectorDB
from app.services.prompt_manager import SYSTEM_PROMPT
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Chat"])
vectordb = VectorDB()

OLLAMA_URL = "http://localhost:11434/api/chat"
# MODEL = "gemma3:270m"
MODEL = "phi4-mini"


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
    logger.info(f"Similarity search results : {len(documents)}")

    # Rerank
    reranked = vectordb.rerank(
        query=request.query,
        documents=documents,
        top_n=3,
    )
    logger.info(f"Vector reraank results : {len(reranked.data)}")

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
    
    formatted_prompt = SYSTEM_PROMPT.format(context=context, question=request.query)

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": formatted_prompt}
        ],
        "stream": False
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
        r = await client.post(OLLAMA_URL, json=payload)
        logger.info(f"{r}")
        data = r.json()
        print(data)
        logger.info(f"{data}")

    return ChatResponse(
        response=markdownify(data["message"]["content"])
    )