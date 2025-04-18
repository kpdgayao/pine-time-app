import secrets
import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, HttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # API configuration
    API_BASE_URL: Optional[str] = None
    
    # Load testing configuration
    LOAD_TEST_MIN_WAIT: Optional[str] = None
    LOAD_TEST_MAX_WAIT: Optional[str] = None
    LOAD_TEST_USER_COUNT: Optional[str] = None
    LOAD_TEST_SPAWN_RATE: Optional[str] = None
    
    # Authentication configuration
    TOKEN_REFRESH_INTERVAL: Optional[str] = None
    AUTH_RETRY_ATTEMPTS: Optional[str] = None
    AUTH_RETRY_DELAY: Optional[str] = None

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and v.startswith("["):
            import json
            return json.loads(v)
        elif isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Pine Time Experience Baguio"
    
    # Database Configuration
    # Database type: "sqlite" or "postgresql"
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "sqlite")
    
    # SQLite Configuration
    SQLITE_DATABASE_URI: str = os.getenv("SQLITE_DATABASE_URI", "sqlite:///./pine_time.db")
    
    # PostgreSQL Configuration
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "pine_time")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_SSL_MODE: str = os.getenv("POSTGRES_SSL_MODE", "prefer")
    
    # Connection pool settings
    POOL_SIZE: int = int(os.getenv("POOL_SIZE", "5"))
    MAX_OVERFLOW: int = int(os.getenv("MAX_OVERFLOW", "10"))
    POOL_TIMEOUT: int = int(os.getenv("POOL_TIMEOUT", "30"))
    POOL_RECYCLE: int = int(os.getenv("POOL_RECYCLE", "1800"))  # 30 minutes
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Get the database URI based on the configured database type.
        """
        if self.DATABASE_TYPE == "postgresql":
            # Add SSL mode if specified
            ssl_query = f"?sslmode={self.POSTGRES_SSL_MODE}" if self.POSTGRES_SSL_MODE else ""
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}{ssl_query}"
        # Default to SQLite
        return self.SQLITE_DATABASE_URI
    
    @property
    def SQLALCHEMY_CONNECT_ARGS(self) -> Dict:
        """
        Get the connection arguments based on the configured database type.
        """
        if self.DATABASE_TYPE == "sqlite":
            return {"check_same_thread": False}
        # PostgreSQL doesn't need special connect args
        return {}
    
    # Users
    FIRST_SUPERUSER: EmailStr = "admin@pinetimeexperience.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin"
    USERS_OPEN_REGISTRATION: bool = False

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from environment variables


settings = Settings()