"""Pytest configuration and fixtures."""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from artomate.core.config import Config
from artomate.db.models import Base, Job, Asset, JobState
from artomate.db.database import Database


@pytest.fixture(scope="session")
def test_config() -> Config:
    """Create test configuration."""
    # Create temporary directory for test data
    temp_dir = tempfile.mkdtemp()

    return Config(
        # Use in-memory SQLite for tests
        database_url="sqlite:///:memory:",
        # Test directories
        assets_dir=Path(temp_dir) / "assets",
        exports_dir=Path(temp_dir) / "exports",
        log_file=Path(temp_dir) / "logs" / "test.log",
        # Test API keys (fake for testing)
        openai_api_key="sk-test-key",
        printify_api_token="test-printify-token",
        printify_shop_id=12345,
        # Test settings
        env="development",
        log_level="DEBUG",
    )


@pytest.fixture(scope="function")
def test_db(test_config: Config) -> Generator[Database, None, None]:
    """Create test database with tables."""
    # Create database
    db = Database(test_config)

    # Create all tables
    Base.metadata.create_all(db.engine)

    yield db

    # Cleanup
    Base.metadata.drop_all(db.engine)
    db.engine.dispose()


@pytest.fixture(scope="function")
def session(test_db: Database) -> Generator[Session, None, None]:
    """Create database session for tests."""
    with test_db.session_scope() as session:
        yield session


@pytest.fixture
def sample_job(session: Session) -> Job:
    """Create a sample job for testing."""
    job = Job(
        theme="test theme",
        style="minimalist",
        keywords=["test", "sample"],
        state=JobState.CREATED,
        niche="home-decor",
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@pytest.fixture
def sample_asset(session: Session, sample_job: Job) -> Asset:
    """Create a sample asset for testing."""
    asset = Asset(
        job_id=sample_job.id,
        asset_type="image",
        storage_path="/tmp/test_image.png",
        url="https://example.com/image.png",
        width=1024,
        height=1024,
        file_size=1024 * 100,  # 100KB
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "created": 1234567890,
        "data": [
            {
                "url": "https://example.com/generated_image.png",
                "revised_prompt": "A minimalist test image",
            }
        ],
    }


@pytest.fixture
def mock_printify_response():
    """Mock Printify API response."""
    return {
        "id": "test-product-id-123",
        "title": "Test Product",
        "description": "Test Description",
        "blueprint_id": 3,
        "print_provider_id": 99,
        "variants": [
            {
                "id": 1,
                "sku": "TEST-SKU",
                "cost": 1500,
                "price": 2500,
                "title": "S / Black",
            }
        ],
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    # Add custom markers
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests",
    )
    config.addinivalue_line(
        "markers",
        "api: marks tests that require API keys",
    )
