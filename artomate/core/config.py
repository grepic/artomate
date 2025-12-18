"""Configuration management using Pydantic settings."""

import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ========================================================================
    # API Keys
    # ========================================================================
    openai_api_key: Optional[str] = None
    stability_api_key: Optional[str] = None
    printify_api_token: Optional[str] = None
    printify_shop_id: Optional[int] = None
    etsy_api_key: Optional[str] = None
    etsy_api_secret: Optional[str] = None
    etsy_shop_id: Optional[int] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[int] = None

    # ========================================================================
    # Database
    # ========================================================================
    database_url: str = Field(default="sqlite:///data/artomate.db")

    # ========================================================================
    # Storage
    # ========================================================================
    assets_dir: Path = Field(default=Path("./data/assets"))
    exports_dir: Path = Field(default=Path("./exports"))

    # S3 (optional)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket: Optional[str] = None
    aws_region: str = "us-east-1"

    # ========================================================================
    # n8n Integration
    # ========================================================================
    n8n_webhook_url: Optional[str] = "http://localhost:5678/webhook/artomate"
    n8n_api_key: Optional[str] = None

    # ========================================================================
    # Application Settings
    # ========================================================================
    env: Literal["development", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_file: Path = Field(default=Path("./logs/artomate.log"))

    # Image Generation
    default_image_provider: Literal["openai", "stability"] = "openai"
    default_image_size: str = "1024x1024"
    default_image_quality: Literal["standard", "hd"] = "hd"

    # Printify Defaults
    default_print_provider_id: int = 99  # Printful
    default_blueprint_ids: str = "3,6,380"  # T-shirt, Poster, Mug

    # Pricing
    markup_percentage: float = 45.0
    minimum_profit: float = 5.00
    round_prices_to: float = 0.99

    # SEO
    seo_title_template: str = "{theme} | {style} | {niche}"
    seo_max_tags: int = 13

    # Daily Automation
    daily_cycle_enabled: bool = False
    daily_cycle_time: str = "03:00"
    daily_cycle_count: int = 10
    daily_cycle_niches: str = "minimalist,boho,japandi,vintage"

    # Rate Limiting
    openai_rpm: int = 50
    printify_rpm: int = 120
    etsy_rpd: int = 10000

    # ========================================================================
    # Feature Flags
    # ========================================================================
    enable_compliance_check: bool = True
    enable_mockup_generation: bool = False
    enable_social_media: bool = False
    enable_stock_platforms: bool = False
    enable_ab_testing: bool = False

    # ========================================================================
    # Security
    # ========================================================================
    api_secret_key: str = "change-this-secret-key"
    api_algorithm: str = "HS256"
    api_access_token_expire_minutes: int = 30

    # ========================================================================
    # Advanced
    # ========================================================================
    max_retries: int = 3
    retry_delay: int = 5
    retry_backoff: float = 2.0
    max_concurrent_jobs: int = 5
    max_concurrent_requests: int = 10
    image_generation_timeout: int = 120
    printify_api_timeout: int = 30
    etsy_api_timeout: int = 30

    @field_validator("assets_dir", "exports_dir", "log_file", mode="before")
    @classmethod
    def ensure_path(cls, v: str | Path) -> Path:
        """Convert string to Path and ensure parent directory exists."""
        path = Path(v) if isinstance(v, str) else v
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def blueprint_ids_list(self) -> list[int]:
        """Parse blueprint IDs from comma-separated string."""
        return [int(x.strip()) for x in self.default_blueprint_ids.split(",")]

    @property
    def niches_list(self) -> list[str]:
        """Parse niches from comma-separated string."""
        return [x.strip() for x in self.daily_cycle_niches.split(",")]

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls()

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for assets
        (self.assets_dir / "images").mkdir(exist_ok=True)
        (self.assets_dir / "videos").mkdir(exist_ok=True)
        (self.assets_dir / "mockups").mkdir(exist_ok=True)
        (self.assets_dir / "printfiles").mkdir(exist_ok=True)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
        _config.ensure_directories()
    return _config
