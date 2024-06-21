from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    project_name: str
    api_version: str

    class Config:
        env_file = ".env"


settings = Settings()
