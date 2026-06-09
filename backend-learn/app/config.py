from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    配置类
    """
    app_name: str = "旅行规划后端"
    app_version: str = "1.0.0"
    debug: bool = True

    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True

    amap_api_key: str = ""

    unsplash_access_key: str = ""
    unsplash_secret_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",             #遇到多余字段不要报错
    )

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    def get_cors_origins(self) -> list[str]:
        # 获取CORS允许的源
        return [origin.strip() for origin in self.cors_origins.split(",") if origin]

settings = Settings()

def get_settings():
    return settings
