from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://inventory:secret@localhost:5432/inventory_db"
    jwt_secret: str = "change-me-to-a-long-random-string-at-least-32-chars"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    default_admin_email: str = "admin@example.com"
    default_admin_password: str = "admin123"
    default_admin_name: str = "System Admin"
    redis_url: str = "redis://localhost:6379"
    sendgrid_api_key: str = ""
    alert_from_email: str = "alerts@inventory-app.com"
    low_stock_function_url: str = ""
    primary_region: str = "yyz"
    environment: str = "production"
    cors_origins: str = "*"

    class Config:
        env_file = ".env"


settings = Settings()
