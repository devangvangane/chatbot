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
    ADMIN_SECRET_KEY: str 

    GEMINI_API_KEY: str
    # GEMINI_NAME: str
    # PROJECT_NAME: str
    # PROJECT_NUMBER: int

    GITHUB_USERNAME: str
    GITHUB_TOKEN: str
    EXCLUDED_REPOS: list = ["https://github.com/devangvangane/aitutor",
        "https://github.com/devangvangane/Anomaly-Tile",
        "https://github.com/devangvangane/clerkaitry",
        "https://github.com/devangvangane/datarecovery",
        "https://github.com/devangvangane/devangvangane",
        "https://github.com/devangvangane/django-react",
        "https://github.com/devangvangane/Django-react-crud",
        "https://github.com/devangvangane/expenseTracker",
        "https://github.com/devangvangane/FrontEndToBackend",
        "https://github.com/devangvangane/hackathontts",
        "https://github.com/devangvangane/hellodjango",
        "https://github.com/devangvangane/Html-file",
        "https://github.com/devangvangane/JavaDSA",
        "https://github.com/devangvangane/music_controller",
        "https://github.com/devangvangane/pratik",
        "https://github.com/devangvangane/pyPortfolio",
        "https://github.com/devangvangane/tts",
        "https://github.com/devangvangane/veerr-doctor",
        "https://github.com/devangvangane/wdproj",
        "https://github.com/devangvangane/week-13-try",
        "https://github.com/devangvangane/week6Streamlit",
        ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


config = Config()