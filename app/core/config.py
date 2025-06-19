from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    MODE: str

    LANGUAGE: str
    MAX_DEPTH: int
    MAX_LINKS_PER_LEVEL: int

    OPENAI_API_KEY: str

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def WIKI_BASE_URL(self):
        return f"https://{self.LANGUAGE}.wikipedia.org"

    model_config = ConfigDict(env_file=".env")


settings = Settings()
