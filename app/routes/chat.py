from fastapi import APIRouter
from pydantic import BaseModel
from google import genai
from google.genai import types
from app.config import config
import asyncio

from app.config import config
from app.services.vectordb_service import VectorDB
from app.services.prompt_manager import SYSTEM_PROMPT
from app.utils.logger import logger
from slowapi import Limiter
from slowapi.util import get_remote_address

client = genai.Client(api_key=config.GEMINI_API_KEY)
router = APIRouter(prefix="/api", tags=["Chat"])
vectordb = VectorDB()

OLLAMA_URL = "http://localhost:11434/api/chat"
# MODEL = "gemma3:270m"
# MODEL = "phi4-mini"

limiter = Limiter(key_func=get_remote_address)



class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    response: str


async def encode(text: str) -> list[float]:
    result = await asyncio.to_thread(
        client.models.embed_content,
        model="gemini-embedding-001",
        contents=text,
    )
    return result.embeddings[0].values


@router.post("/chat")
@limiter.limit("10/minute")
async def chat(request: ChatRequest):

    # Generate query embedding
    query_embedding = await encode(request.query)

    # Search Pinecone
    search_results = await vectordb.search(
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
    reranked = await vectordb.rerank(
        query=request.query,
        documents=documents,
        top_n=3,
    )
    logger.info(f"Vector rerank results : {len(reranked.data)}")

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
    
    formatted_prompt = SYSTEM_PROMPT.format(context=context, question=request.query, creator_name="Devang")

    # payload = {
    #     "model": MODEL,
    #     "messages": [
    #         {"role": "user", "content": formatted_prompt}
    #     ],
    #     "stream": False,
    #      "options": {
    #         "temperature": 0.3
    #     }
    # }

    response = await asyncio.to_thread(
        client.models.generate_content,
        model="gemini-2.5-flash",
        contents=formatted_prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=300
        )
    )
    logger.info(f"{response.text}")

    return ChatResponse(
        response=response.text
    )