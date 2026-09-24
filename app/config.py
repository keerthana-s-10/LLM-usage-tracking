from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://metering:metering@localhost:5432/metering"
    port: int = 8000
    stripe_secret_key: str = "sk_test_replace_me"
    stripe_webhook_secret: str = "whsec_replace_me"
    stripe_price_id: str = "price_replace_me"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
