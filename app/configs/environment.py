from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    db_url: str = Field(..., env='DATABASE_URL')
    secret_key: str = Field(..., env='SECRET_KEY')
    algorithm: str = Field(..., env='ALGORITHM')
    environment: str = Field(..., env="ENVIRONMENT")
    current_domain: str = Field(..., env="CURRENT_DOMAIN")


env: Settings = Settings()
