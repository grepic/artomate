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

    # ========================================================================
    # Configuration Validation
    # ========================================================================

    def validate_for_image_generation(self) -> None:
        """Validate configuration for image generation.

        Raises:
            ValueError: If required settings are missing
        """
        if self.default_image_provider == "openai":
            if not self.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY is required for image generation with OpenAI. "
                    "Set it in .env file or environment variables."
                )
        elif self.default_image_provider == "stability":
            if not self.stability_api_key:
                raise ValueError(
                    "STABILITY_API_KEY is required for image generation with Stability AI. "
                    "Set it in .env file or environment variables."
                )

    def validate_for_printify(self) -> None:
        """Validate configuration for Printify integration.

        Raises:
            ValueError: If required settings are missing
        """
        if not self.printify_api_token:
            raise ValueError(
                "PRINTIFY_API_TOKEN is required for Printify integration. "
                "Get your API token from https://printify.com/app/account/api"
            )
        if not self.printify_shop_id:
            raise ValueError(
                "PRINTIFY_SHOP_ID is required for Printify integration. "
                "Find your shop ID in Printify dashboard."
            )

    def validate_for_etsy(self) -> None:
        """Validate configuration for Etsy integration.

        Raises:
            ValueError: If required settings are missing
        """
        if not self.etsy_api_key:
            raise ValueError(
                "ETSY_API_KEY is required for Etsy integration. "
                "Create an app at https://www.etsy.com/developers/your-apps"
            )
        if not self.etsy_shop_id:
            raise ValueError(
                "ETSY_SHOP_ID is required for Etsy integration. "
                "Find your shop ID in Etsy dashboard."
            )

    def validate_for_telegram(self) -> None:
        """Validate configuration for Telegram bot.

        Raises:
            ValueError: If required settings are missing
        """
        if not self.telegram_bot_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN is required for Telegram integration. "
                "Create a bot with @BotFather on Telegram."
            )

    def validate_for_storage(self) -> None:
        """Validate storage configuration.

        Raises:
            ValueError: If storage paths are not writable
        """
        # Check if directories exist and are writable
        try:
            self.ensure_directories()
        except PermissionError as e:
            raise ValueError(f"Storage directory is not writable: {e}")

        # Check disk space (at least 1GB free)
        import shutil
        stat = shutil.disk_usage(self.assets_dir)
        free_gb = stat.free / (1024 ** 3)
        if free_gb < 1.0:
            raise ValueError(
                f"Insufficient disk space: {free_gb:.2f}GB free. "
                "At least 1GB required for asset storage."
            )

    def validate_for_database(self) -> None:
        """Validate database configuration.

        Raises:
            ValueError: If database configuration is invalid
        """
        if not self.database_url:
            raise ValueError("DATABASE_URL is required")

        # For SQLite, ensure directory exists
        if self.database_url.startswith("sqlite:///"):
            db_path = Path(self.database_url.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)

    def validate_complete_workflow(self) -> None:
        """Validate all required settings for complete workflow.

        This validates everything needed to run a full content-to-commerce workflow:
        - Image generation
        - Printify product creation
        - Storage
        - Database

        Raises:
            ValueError: If any required settings are missing
        """
        errors = []

        # Validate each component
        try:
            self.validate_for_image_generation()
        except ValueError as e:
            errors.append(f"Image generation: {e}")

        try:
            self.validate_for_printify()
        except ValueError as e:
            errors.append(f"Printify: {e}")

        try:
            self.validate_for_storage()
        except ValueError as e:
            errors.append(f"Storage: {e}")

        try:
            self.validate_for_database()
        except ValueError as e:
            errors.append(f"Database: {e}")

        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(
                f"  - {error}" for error in errors
            )
            raise ValueError(error_msg)

    def get_missing_optional_configs(self) -> list[str]:
        """Get list of optional configurations that are not set.

        Returns:
            List of missing optional configuration keys
        """
        missing = []

        if not self.etsy_api_key:
            missing.append("ETSY_API_KEY (required for Etsy listings)")
        if not self.telegram_bot_token:
            missing.append("TELEGRAM_BOT_TOKEN (required for Telegram bot)")
        if not self.stability_api_key and self.default_image_provider == "stability":
            missing.append("STABILITY_API_KEY (alternative to OpenAI)")
        if not self.aws_access_key_id:
            missing.append("AWS_ACCESS_KEY_ID (optional for S3 storage)")
        if not self.n8n_api_key:
            missing.append("N8N_API_KEY (optional for n8n integration)")

        return missing

    def print_validation_status(self) -> None:
        """Print configuration validation status to console."""
        print("\n" + "=" * 60)
        print("🔧 Configuration Validation Status")
        print("=" * 60)

        # Check core requirements
        checks = {
            "Image Generation": self._check_image_generation,
            "Printify": self._check_printify,
            "Storage": self._check_storage,
            "Database": self._check_database,
            "Etsy (optional)": self._check_etsy,
            "Telegram (optional)": self._check_telegram,
        }

        for name, check_func in checks.items():
            try:
                check_func()
                print(f"✅ {name:<25} OK")
            except ValueError as e:
                print(f"❌ {name:<25} MISSING")

        # Show missing optional configs
        missing = self.get_missing_optional_configs()
        if missing:
            print("\n💡 Optional configurations not set:")
            for item in missing:
                print(f"   - {item}")

        print("=" * 60 + "\n")

    def _check_image_generation(self):
        self.validate_for_image_generation()

    def _check_printify(self):
        self.validate_for_printify()

    def _check_storage(self):
        self.validate_for_storage()

    def _check_database(self):
        self.validate_for_database()

    def _check_etsy(self):
        self.validate_for_etsy()

    def _check_telegram(self):
        self.validate_for_telegram()


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
        _config.ensure_directories()
    return _config
