"""Tests for configuration."""

import pytest
from pathlib import Path

from artomate.core.config import Config


class TestConfig:
    """Test configuration management."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = Config()

        assert config.env == "development"
        assert config.log_level == "INFO"
        assert config.default_image_provider == "openai"
        assert config.default_image_quality == "hd"
        assert config.markup_percentage == 45.0

    def test_config_from_env(self, monkeypatch):
        """Test loading configuration from environment variables."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("ENV", "production")

        config = Config()

        assert config.openai_api_key == "test-key-123"
        assert config.log_level == "DEBUG"
        assert config.env == "production"

    def test_validate_for_image_generation_openai_success(self):
        """Test image generation validation with OpenAI."""
        config = Config(
            openai_api_key="test-key",
            default_image_provider="openai",
        )

        # Should not raise
        config.validate_for_image_generation()

    def test_validate_for_image_generation_openai_missing_key(self):
        """Test image generation validation with missing OpenAI key."""
        config = Config(
            openai_api_key=None,
            default_image_provider="openai",
        )

        with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
            config.validate_for_image_generation()

    def test_validate_for_printify_success(self):
        """Test Printify validation with valid config."""
        config = Config(
            printify_api_token="test-token",
            printify_shop_id=123,
        )

        # Should not raise
        config.validate_for_printify()

    def test_validate_for_printify_missing_token(self):
        """Test Printify validation with missing token."""
        config = Config(printify_api_token=None)

        with pytest.raises(ValueError, match="PRINTIFY_API_TOKEN is required"):
            config.validate_for_printify()

    def test_validate_for_printify_missing_shop_id(self):
        """Test Printify validation with missing shop ID."""
        config = Config(
            printify_api_token="test-token",
            printify_shop_id=None,
        )

        with pytest.raises(ValueError, match="PRINTIFY_SHOP_ID is required"):
            config.validate_for_printify()

    def test_validate_for_etsy_missing_keys(self):
        """Test Etsy validation with missing keys."""
        config = Config(etsy_api_key=None)

        with pytest.raises(ValueError, match="ETSY_API_KEY is required"):
            config.validate_for_etsy()

    def test_validate_for_telegram_missing_token(self):
        """Test Telegram validation with missing token."""
        config = Config(telegram_bot_token=None)

        with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is required"):
            config.validate_for_telegram()

    def test_validate_for_database_sqlite(self):
        """Test database validation with SQLite."""
        config = Config(database_url="sqlite:///data/test.db")

        # Should not raise
        config.validate_for_database()

    def test_validate_complete_workflow_success(self):
        """Test complete workflow validation with all required settings."""
        config = Config(
            openai_api_key="test-key",
            printify_api_token="test-token",
            printify_shop_id=123,
            database_url="sqlite:///:memory:",
        )

        # Should not raise
        config.validate_complete_workflow()

    def test_validate_complete_workflow_missing_configs(self):
        """Test complete workflow validation with missing configs."""
        config = Config(
            openai_api_key=None,  # Missing
            printify_api_token=None,  # Missing
        )

        with pytest.raises(ValueError, match="Configuration validation failed"):
            config.validate_complete_workflow()

    def test_get_missing_optional_configs(self):
        """Test getting list of missing optional configs."""
        config = Config(
            openai_api_key="test-key",
            etsy_api_key=None,
            telegram_bot_token=None,
        )

        missing = config.get_missing_optional_configs()

        assert "ETSY_API_KEY" in str(missing)
        assert "TELEGRAM_BOT_TOKEN" in str(missing)

    def test_blueprint_ids_list_property(self):
        """Test parsing blueprint IDs from comma-separated string."""
        config = Config(default_blueprint_ids="3,6,380")

        blueprint_ids = config.blueprint_ids_list

        assert blueprint_ids == [3, 6, 380]
        assert isinstance(blueprint_ids[0], int)

    def test_niches_list_property(self):
        """Test parsing niches from comma-separated string."""
        config = Config(daily_cycle_niches="minimalist,boho,japandi")

        niches = config.niches_list

        assert niches == ["minimalist", "boho", "japandi"]
        assert isinstance(niches[0], str)

    def test_ensure_directories_creates_structure(self, tmp_path):
        """Test that ensure_directories creates required directory structure."""
        config = Config(
            assets_dir=tmp_path / "assets",
            exports_dir=tmp_path / "exports",
            log_file=tmp_path / "logs" / "test.log",
        )

        config.ensure_directories()

        # Check main directories
        assert (tmp_path / "assets").exists()
        assert (tmp_path / "exports").exists()
        assert (tmp_path / "logs").exists()

        # Check asset subdirectories
        assert (tmp_path / "assets" / "images").exists()
        assert (tmp_path / "assets" / "videos").exists()
        assert (tmp_path / "assets" / "mockups").exists()
        assert (tmp_path / "assets" / "printfiles").exists()
