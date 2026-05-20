from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI 求职助手"
    debug: bool = False

    # DeepSeek
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # CORS — 逗号分隔的允许来源列表
    cors_origins: str = "http://localhost:3000"

    # Database (reserved for future use)
    database_url: str = ""

    # Supabase
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # Lemon Squeezy — 直接支付链接 + Webhook
    lemon_squeezy_checkout_url: str = ""
    lemon_squeezy_checkout_url_yearly: str = ""
    lemon_squeezy_webhook_secret: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
