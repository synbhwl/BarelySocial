from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEBUG: bool = True
    ENVIRONMENT: str = "local"
    JWT_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()