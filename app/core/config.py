# Update imports for Pydantic v2
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "placeholder_secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        extra = "ignore"
        
    @property
    def get_database_url(self) -> str:
        # Step 3: Neon SSL Compatibility
        url = self.DATABASE_URL
        if "neon.tech" in url and "sslmode=require" not in url:
            if "?" in url:
                url += "&sslmode=require"
            else:
                url += "?sslmode=require"
        return url


settings = Settings()
