from pydantic import BaseSettings

class Settings(BaseSettings):
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    chroma_dir: str = "/data/chroma"

    openai_api_key: str = None
    embedding_model: str = "text-embedding-3-small"
    llm_api_url: str = None
    llm_model: str = None

    max_documents: int = 20
    max_pages_per_doc: int = 1000
    chunk_size: int = 1000
    chunk_overlap: int = 200

    class Config:
        env_file = ".env"

settings = Settings()
