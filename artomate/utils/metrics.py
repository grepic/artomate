"""Prometheus metrics for monitoring."""

from prometheus_client import Counter, Histogram, Gauge, Info

# ============================================================================
# Job Metrics
# ============================================================================

# Job counters
jobs_created_total = Counter(
    "artomate_jobs_created_total",
    "Total number of jobs created",
)

jobs_completed_total = Counter(
    "artomate_jobs_completed_total",
    "Total number of jobs completed",
    ["status"],  # Labels: success, failed
)

jobs_failed_total = Counter(
    "artomate_jobs_failed_total",
    "Total number of jobs that failed",
    ["state"],  # Label: state where it failed
)

# Job duration histogram
job_duration_seconds = Histogram(
    "artomate_job_duration_seconds",
    "Job execution duration in seconds",
    ["job_type"],  # Label: complete_workflow, image_only, etc.
    buckets=[30, 60, 120, 300, 600, 1200, 1800, 3600],  # 30s to 1h
)

# Active jobs gauge
active_jobs = Gauge(
    "artomate_active_jobs",
    "Number of currently active jobs",
)

# ============================================================================
# Image Generation Metrics
# ============================================================================

images_generated_total = Counter(
    "artomate_images_generated_total",
    "Total number of images generated",
    ["provider"],  # Labels: openai, stability
)

image_generation_duration_seconds = Histogram(
    "artomate_image_generation_duration_seconds",
    "Image generation duration in seconds",
    ["provider"],
    buckets=[5, 10, 20, 30, 60, 120],
)

image_generation_failures_total = Counter(
    "artomate_image_generation_failures_total",
    "Total number of image generation failures",
    ["provider", "error_type"],
)

# ============================================================================
# Product Creation Metrics
# ============================================================================

products_created_total = Counter(
    "artomate_products_created_total",
    "Total number of products created",
    ["platform", "product_type"],  # platforms: printify, etsy
)

product_creation_duration_seconds = Histogram(
    "artomate_product_creation_duration_seconds",
    "Product creation duration in seconds",
    ["platform"],
    buckets=[1, 2, 5, 10, 30, 60],
)

product_creation_failures_total = Counter(
    "artomate_product_creation_failures_total",
    "Total number of product creation failures",
    ["platform"],
)

# ============================================================================
# Social Media Metrics
# ============================================================================

social_posts_created_total = Counter(
    "artomate_social_posts_created_total",
    "Total number of social media posts created",
    ["platform"],  # Platforms: instagram, tiktok, youtube
)

social_posts_failures_total = Counter(
    "artomate_social_posts_failures_total",
    "Total number of social post failures",
    ["platform"],
)

# ============================================================================
# Queue Metrics
# ============================================================================

queue_length = Gauge(
    "artomate_queue_length",
    "Number of jobs in queue",
    ["queue_name"],
)

queue_workers = Gauge(
    "artomate_queue_workers",
    "Number of active queue workers",
)

# ============================================================================
# API Metrics
# ============================================================================

api_requests_total = Counter(
    "artomate_api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status_code"],
)

api_request_duration_seconds = Histogram(
    "artomate_api_request_duration_seconds",
    "API request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

# ============================================================================
# System Metrics
# ============================================================================

system_info = Info(
    "artomate_system",
    "System information",
)

database_connections = Gauge(
    "artomate_database_connections",
    "Number of active database connections",
)

storage_free_gb = Gauge(
    "artomate_storage_free_gb",
    "Free storage space in GB",
)

storage_used_percent = Gauge(
    "artomate_storage_used_percent",
    "Storage space used in percent",
)

# ============================================================================
# Helper Functions
# ============================================================================


def track_job_created():
    """Track job creation."""
    jobs_created_total.inc()
    active_jobs.inc()


def track_job_completed(success: bool, state: str = None):
    """Track job completion.

    Args:
        success: Whether job completed successfully
        state: State where job failed (if failed)
    """
    active_jobs.dec()

    if success:
        jobs_completed_total.labels(status="success").inc()
    else:
        jobs_completed_total.labels(status="failed").inc()
        if state:
            jobs_failed_total.labels(state=state).inc()


def track_image_generated(provider: str, duration: float):
    """Track image generation.

    Args:
        provider: Provider name (openai, stability)
        duration: Generation duration in seconds
    """
    images_generated_total.labels(provider=provider).inc()
    image_generation_duration_seconds.labels(provider=provider).observe(duration)


def track_image_generation_failure(provider: str, error_type: str):
    """Track image generation failure.

    Args:
        provider: Provider name
        error_type: Type of error
    """
    image_generation_failures_total.labels(
        provider=provider,
        error_type=error_type,
    ).inc()


def track_product_created(platform: str, product_type: str, duration: float):
    """Track product creation.

    Args:
        platform: Platform name (printify, etsy)
        product_type: Product type
        duration: Creation duration in seconds
    """
    products_created_total.labels(
        platform=platform,
        product_type=product_type,
    ).inc()
    product_creation_duration_seconds.labels(platform=platform).observe(duration)


def track_product_creation_failure(platform: str):
    """Track product creation failure.

    Args:
        platform: Platform name
    """
    product_creation_failures_total.labels(platform=platform).inc()


def track_social_post_created(platform: str):
    """Track social media post creation.

    Args:
        platform: Platform name
    """
    social_posts_created_total.labels(platform=platform).inc()


def track_social_post_failure(platform: str):
    """Track social media post failure.

    Args:
        platform: Platform name
    """
    social_posts_failures_total.labels(platform=platform).inc()


def update_queue_metrics(queue_stats: dict):
    """Update queue metrics from stats.

    Args:
        queue_stats: Queue statistics dict
    """
    queue_length.labels(queue_name=queue_stats.get("queue_name", "artomate")).set(
        queue_stats.get("queued", 0)
    )
    queue_workers.set(queue_stats.get("workers", 0))


def update_storage_metrics(free_gb: float, used_percent: float):
    """Update storage metrics.

    Args:
        free_gb: Free space in GB
        used_percent: Used space in percent
    """
    storage_free_gb.set(free_gb)
    storage_used_percent.set(used_percent)
