from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router
from app.routes.knowledge_base import router as kb_router


origins = [
    # "http://localhost:5173"
    "https://devangv.netlify.app"
]

app = FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=False,
                   allow_methods=["*"],
                   allow_headers=["*"]
)

app.include_router(router)
app.include_router(kb_router)