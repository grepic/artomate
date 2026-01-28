"""Extended database models for advanced features."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .models import Base


# ============================================================================
# Enums
# ============================================================================


class StockPlatform(str, enum.Enum):
    """Stock platform types."""
    
    # Premium platforms
    SHUTTERSTOCK = "shutterstock"
    ADOBE_STOCK = "adobe_stock"
    GETTY_IMAGES = "getty_images"
    ISTOCK = "istock"
    DEPOSITPHOTOS = "depositphotos"
    
    # Free platforms
    UNSPLASH = "unsplash"
    PEXELS = "pexels"
    PIXABAY = "pixabay"
    
    # Specialized
    FIVEHUNDREDPX = "500px"
    DREAMSTIME = "dreamstime"
    ALAMY = "alamy"
    POND5 = "pond5"
    
    # Digital marketplaces
    ETSY_DIGITAL = "etsy_digital"
    CREATIVE_MARKET = "creative_market"
    CREATIVE_FABRICA = "creative_fabrica"
    
    # Print-on-demand
    REDBUBBLE = "redbubble"
    SOCIETY6 = "society6"
    EYEEM = "eyeem"


class SubmissionStatus(str, enum.Enum):
    """Stock submission status."""
    
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    LIVE = "live"
    FAILED = "failed"


class PublicationStatus(str, enum.Enum):
    """Publication status."""
    
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# Models
# ============================================================================


class Collection(Base):
    """Collection of related designs/products."""
    
    __tablename__ = "collections"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    
    # Collection info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    theme: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)
    
    # Organization
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_campaign: Mapped[bool] = mapped_column(Boolean, default=False)
    campaign_dates: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Assets
    cover_image_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    job_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)
    
    # Metadata
    metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    # Relationships
    submissions: Mapped[list["StockSubmission"]] = relationship(
        "StockSubmission", back_populates="collection"
    )
    
    def __repr__(self) -> str:
        return f"<Collection(id={self.id}, name='{self.name}')>"


class StockSubmission(Base):
    """Stock platform submission tracking."""
    
    __tablename__ = "stock_submissions"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    collection_id: Mapped[Optional[int]] = mapped_column(ForeignKey("collections.id"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Platform
    platform: Mapped[StockPlatform] = mapped_column(Enum(StockPlatform), nullable=False)
    platform_submission_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    platform_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus), default=SubmissionStatus.DRAFT, nullable=False
    )
    status_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    keywords: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)
    categories: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)
    
    # SEO
    seo_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seo_tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)
    
    # Performance
    downloads_count: Mapped[int] = mapped_column(Integer, default=0)
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    earnings: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Review history
    review_notes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)
    rejection_reasons: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)
    
    # Submission data
    submission_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    # Relationships
    collection: Mapped[Optional["Collection"]] = relationship("Collection", back_populates="submissions")
    
    def __repr__(self) -> str:
        return f"<StockSubmission(id={self.id}, platform={self.platform}, status={self.status})>"


class ScheduledPublication(Base):
    """Scheduled publications (social, stock, marketplaces)."""
    
    __tablename__ = "scheduled_publications"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    scheduled_for: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Publication type
    publication_type: Mapped[str] = mapped_column(String(50), nullable=False)  # social, stock, marketplace
    
    # Status
    status: Mapped[PublicationStatus] = mapped_column(
        Enum(PublicationStatus), default=PublicationStatus.SCHEDULED, nullable=False
    )
    
    # Configuration
    target_platforms: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    publication_config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    # Content
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    # Results
    results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)
    errors: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)
    
    # Retry
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    def __repr__(self) -> str:
        return f"<ScheduledPublication(id={self.id}, type={self.publication_type}, status={self.status})>"


class PlatformCredentials(Base):
    """API credentials for different platforms."""
    
    __tablename__ = "platform_credentials"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    
    # Platform identification
    platform_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    platform_type: Mapped[str] = mapped_column(String(50), nullable=False)  # social, stock, marketplace
    
    # Credentials (encrypted)
    api_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    api_secret: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # OAuth data
    oauth_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Additional config
    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    def __repr__(self) -> str:
        return f"<PlatformCredentials(platform={self.platform_name}, active={self.is_active})>"


class AnalyticsSnapshot(Base):
    """Daily analytics snapshots for performance tracking."""
    
    __tablename__ = "analytics_snapshots"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamps
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Target entity
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Metrics
    views: Mapped[int] = mapped_column(Integer, default=0)
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    favorites: Mapped[int] = mapped_column(Integer, default=0)
    sales: Mapped[int] = mapped_column(Integer, default=0)
    revenue: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Platform-specific metrics
    platform_metrics: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    # Metadata
    metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    def __repr__(self) -> str:
        return f"<AnalyticsSnapshot(entity={self.entity_type}:{self.entity_id}, date={self.snapshot_date})>"
