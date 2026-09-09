from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vault API"

    database_url: str
    
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

settings = Settings()