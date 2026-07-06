from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    PINECONE_DIMENSION: int = 768
    PINECONE_METRIC: str = "cosine"
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"

    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"

    YOUTUBE_CHANNEL_NAME: str

    GEMINI_API_KEY: str
    GEMINI_NAME: str
    PROJECT_NAME: str
    PROJECT_NUMBER: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


config = Config()