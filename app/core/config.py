from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "placeholder_secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CLERK_WEBHOOK_SECRET: str = "whsec_placeholder"
    CLERK_SECRET_KEY: str = "sk_test_placeholder"
    CLERK_JWKS_URL: str = "https://summary-lioness-53.clerk.accounts.dev/.well-known/jwks.json"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
        extra="ignore"
    )
        
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
