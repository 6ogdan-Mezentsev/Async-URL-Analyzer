from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    postgres_user: str = os.getenv("POSTGRES_USER")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD")
    postgres_db: str = os.getenv("POSTGRES_DB")
    postgres_host: str = os.getenv("POSTGRES_HOST")
    postgres_port: str = os.getenv("POSTGRES_PORT")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return os.getenv("REDIS_URL")


settings = Settings()
