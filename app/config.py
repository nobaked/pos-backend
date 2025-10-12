from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # Database
    DATABASE_URL: str
    
    # CORS
    CORS_ORIGINS: str
    
    # Application
    ENV: str = "development"
    SECRET_KEY: str = "dev_secret_key"
    DEBUG: bool = True
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    
    # Performance
    WORKERS_PER_CORE: int = 2
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        """CORS_ORIGINSを文字列からリストに変換"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]


# 設定のインスタンスを作成
settings = Settings()

# 互換性のため（古いコードが使っている可能性）
DATABASE_URL = settings.DATABASE_URL
CORS_ORIGINS = settings.cors_origins_list
ENV = settings.ENV
SECRET_KEY = settings.SECRET_KEY
DEBUG = settings.DEBUG
LOG_LEVEL = settings.LOG_LEVEL
WORKERS_PER_CORE = settings.WORKERS_PER_CORE
