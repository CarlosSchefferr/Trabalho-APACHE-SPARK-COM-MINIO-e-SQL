from __future__ import annotations

from dataclasses import dataclass, field
import os


@dataclass(frozen=True)
class Settings:
    postgres_host: str = field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    postgres_port: str = field(default_factory=lambda: os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = field(default_factory=lambda: os.getenv("POSTGRES_DB", "trabalho2"))
    postgres_user: str = field(default_factory=lambda: os.getenv("POSTGRES_USER", "postgres"))
    postgres_password: str = field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", "postgres"))
    minio_endpoint: str = field(default_factory=lambda: os.getenv("MINIO_ENDPOINT", "http://localhost:9000"))
    minio_region: str = field(default_factory=lambda: os.getenv("MINIO_REGION", "us-east-1"))
    minio_access_key: str = field(default_factory=lambda: os.getenv("MINIO_ROOT_USER", "minioadmin"))
    minio_secret_key: str = field(default_factory=lambda: os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"))
    landing_bucket: str = field(default_factory=lambda: os.getenv("LANDING_BUCKET", "landing-zone"))
    bronze_bucket: str = field(default_factory=lambda: os.getenv("BRONZE_BUCKET", "bronze"))
    spark_app_name: str = field(default_factory=lambda: os.getenv("SPARK_APP_NAME", "trabalho2-spark-minio-delta"))

    @property
    def jdbc_url(self) -> str:
        return (
            f"jdbc:postgresql://{self.postgres_host}:{self.postgres_port}/"
            f"{self.postgres_db}"
        )


def get_settings() -> Settings:
    return Settings()
