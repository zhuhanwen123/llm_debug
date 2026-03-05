from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Multi LLM Gateway"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    db_host: str = "mysql"
    db_port: int = 3306
    db_name: str = "llm_platform"
    db_user: str = "llm_user"
    db_password: str = "llm_pass"

    upload_dir: str = "/app/uploads"
    public_base_url: str = ""

    access_token: str = "change-me"
    master_key: str = ""

    cors_origins: str = "*"
    default_timeout_ms: int = 60000

    default_mock_video_url: str = "https://samplelib.com/lib/preview/mp4/sample-5s.mp4"

    oss_endpoint: str = "test"
    oss_bucket: str = "test"
    oss_access_key_id: str = "test"
    oss_access_key_secret: str = "test"
    oss_prefix: str = "test"
    oss_public_base_url: str = "test"

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()
