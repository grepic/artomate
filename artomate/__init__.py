"""Artomate - Content-to-Commerce Automation System."""

__version__ = "0.1.0"
__author__ = "Artomate Team"

from artomate.core.config import Config, get_config
from artomate.core.job_manager import JobManager
from artomate.db.database import get_db, init_db
from artomate.db.models import Job, Asset, Product, JobState, AssetType

__all__ = [
    "Config",
    "get_config",
    "JobManager",
    "get_db",
    "init_db",
    "Job",
    "Asset",
    "Product",
    "JobState",
    "AssetType",
]
