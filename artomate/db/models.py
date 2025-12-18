"""SQLAlchemy database models."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


# ============================================================================
# Enums
# ============================================================================


class JobState(str, enum.Enum):
    """Job state machine states."""

    CREATED = "created"
    PROCESSING_INPUT = "processing_input"
    GENERATING = "generating"
    RENDERING = "rendering"
    PRINTIFY_UPLOAD = "printify_upload"
    PRINTIFY_PRODUCT = "printify_product"
    ETSY_LISTING = "etsy_listing"
    SOCIAL_PUBLISHING = "social_publishing"
    STOCK_SUBMITTING = "stock_submitting"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AssetType(str, enum.Enum):
    """Asset type classification."""

    HERO = "hero"  # Main generated image
    PATTERN = "pattern"  # Seamless pattern
    VARIANT = "variant"  # Color/style variant
    MOCKUP = "mockup"  # Product mockup
    VIDEO = "video"  # Social media video
    PRINTFILE = "printfile"  # Print-ready file


class MarketplaceType(str, enum.Enum):
    """Marketplace platforms."""

    ETSY = "etsy"
    SHOPIFY = "shopify"
    AMAZON = "amazon"
    EBAY = "ebay"


class SocialPlatform(str, enum.Enum):
    """Social media platforms."""

    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    PINTEREST = "pinterest"
    FACEBOOK = "facebook"


# ============================================================================
# Models
# ============================================================================


class Job(Base):
    """Main job tracking table."""

    __tablename__ = "jobs"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # State management
    state: Mapped[JobState] = mapped_column(
        Enum(JobState), default=JobState.CREATED, nullable=False
    )
    state_history: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

    # Input configuration
    input_source: Mapped[str] = mapped_column(String(50), nullable=False)  # manual, csv, trend
    input_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Theme/Concept
    theme: Mapped[str] = mapped_column(String(255), nullable=False)
    niche: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    style: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    keywords: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)

    # Configuration
    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Workflow tracking
    current_step: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_log: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)

    # Metadata
    priority: Mapped[int] = mapped_column(Integer, default=5)
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="job", cascade="all, delete-orphan")
    products: Mapped[list["Product"]] = relationship("Product", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, theme='{self.theme}', state={self.state})>"


class Asset(Base):
    """Generated assets (images, videos)."""

    __tablename__ = "assets"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Asset type
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType), nullable=False)
    subtype: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Storage
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    storage_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Image metadata
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    format: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    color_palette: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Generation metadata
    generator: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generation_params: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Compliance
    compliance_checked: Mapped[bool] = mapped_column(Boolean, default=False)
    compliance_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    compliance_issues: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Usage tracking
    used_in_products: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="assets")
    print_files: Mapped[list["PrintFile"]] = relationship(
        "PrintFile", back_populates="asset", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Asset(id={self.id}, type={self.asset_type}, path='{self.storage_path}')>"


class PrintFile(Base):
    """Rendered print-ready files for specific dimensions."""

    __tablename__ = "print_files"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Target specifications
    target_width: Mapped[int] = mapped_column(Integer, nullable=False)
    target_height: Mapped[int] = mapped_column(Integer, nullable=False)
    dpi: Mapped[int] = mapped_column(Integer, default=300)
    color_mode: Mapped[str] = mapped_column(String(20), default="RGB")

    # Rendering strategy
    crop_mode: Mapped[str] = mapped_column(String(20), nullable=False)  # contain, cover, smart_crop
    print_area_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Storage
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    storage_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Printify mapping
    printify_blueprint_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    printify_print_provider_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    printify_variant_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="print_files")

    def __repr__(self) -> str:
        return f"<PrintFile(id={self.id}, size={self.target_width}x{self.target_height})>"


class Product(Base):
    """Printify products."""

    __tablename__ = "products"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Product identity
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)

    # Printify
    printify_product_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    printify_blueprint_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    printify_shop_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    printify_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Pricing
    base_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    selling_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    profit_margin: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Assets
    primary_asset_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mockup_asset_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)
    print_file_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)

    # Metadata
    product_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="products")
    listings: Mapped[list["MarketplaceListing"]] = relationship(
        "MarketplaceListing", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, title='{self.title}')>"


class MarketplaceListing(Base):
    """Marketplace listings (Etsy, Shopify, etc.)."""

    __tablename__ = "marketplace_listings"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Marketplace
    marketplace: Mapped[MarketplaceType] = mapped_column(Enum(MarketplaceType), nullable=False)
    marketplace_listing_id: Mapped[Optional[str]] = mapped_column(String(200), unique=True, nullable=True)

    # Listing details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)
    category: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # SEO
    seo_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    seo_keywords: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)

    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    listing_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Images
    image_urls: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)

    # Pricing
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Performance (denormalized)
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    favorites_count: Mapped[int] = mapped_column(Integer, default=0)
    orders_count: Mapped[int] = mapped_column(Integer, default=0)
    revenue: Mapped[float] = mapped_column(Float, default=0.0)

    # Metadata
    listing_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="listings")

    def __repr__(self) -> str:
        return f"<MarketplaceListing(id={self.id}, marketplace={self.marketplace}, title='{self.title}')>"


class SocialPost(Base):
    """Social media posts."""

    __tablename__ = "social_posts"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Platform
    platform: Mapped[SocialPlatform] = mapped_column(Enum(SocialPlatform), nullable=False)
    platform_post_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Content
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hashtags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)
    video_asset_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    image_asset_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=list)

    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="scheduled")
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Performance
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    shares_count: Mapped[int] = mapped_column(Integer, default=0)

    # Metadata
    post_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"<SocialPost(id={self.id}, platform={self.platform}, status={self.status})>"


class PerformanceMetric(Base):
    """Performance tracking metrics."""

    __tablename__ = "performance_metrics"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Timestamps
    recorded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Target entity
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Metrics
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Extra data
    extra_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"<PerformanceMetric(entity={self.entity_type}:{self.entity_id}, metric={self.metric_name}={self.metric_value})>"
