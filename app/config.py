from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #Application Config
    APP_ENV: str = "development"

    #EvolutionAPI config
    EVOLUTION_API_URL: str
    EVOLUTION_INSTANCE_NAME: str
    EVOLUTION_API_KEY: str
    ALLOWED_GROUP_JID: str
    DEFAULT_DESTINATION: str

    #Shopee Config
    SHOPEE_API_URL: str = "https://open-api.shopee.com.br"
    SHOPEE_APP_ID: str = ""
    SHOPEE_SECRET_KEY: str = ""

    #Redis Config
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

settings = Settings()

# Debug: Mostrar valores carregados
print("\n" + "="*60)
print("🔍 [CONFIG DEBUG]")
print("="*60)
print(f"App ID: '{settings.SHOPEE_APP_ID}' (len={len(settings.SHOPEE_APP_ID)})")
print(f"App ID (repr): {repr(settings.SHOPEE_APP_ID)}")
print(f"App ID (bytes): {settings.SHOPEE_APP_ID.encode('utf-8')}")
print()
print(f"Secret Key: '{settings.SHOPEE_SECRET_KEY[:10]}...' (len={len(settings.SHOPEE_SECRET_KEY)})")
print(f"Secret Key (repr): {repr(settings.SHOPEE_SECRET_KEY)}")
print(f"Secret Key (bytes): {settings.SHOPEE_SECRET_KEY.encode('utf-8')}")
print()
print(f"API URL: {settings.SHOPEE_API_URL}")
print("="*60 + "\n")
