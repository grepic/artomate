"""Prometheus metrics endpoint."""

import shutil
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from artomate.core.config import get_config
from artomate.workers.queue import get_queue
from artomate.utils.metrics import update_queue_metrics, update_storage_metrics

router = APIRouter()


@router.get("")
async def metrics_endpoint():
    """Prometheus metrics endpoint.

    Returns metrics in Prometheus text format.

    Usage:
        Add to prometheus.yml:
        ```yaml
        scrape_configs:
          - job_name: 'artomate'
            static_configs:
              - targets: ['localhost:8000']
            metrics_path: '/metrics'
        ```
    """
    # Update dynamic metrics before generating output
    try:
        # Update queue metrics
        queue = get_queue()
        if queue.is_available():
            queue_stats = queue.get_stats()
            update_queue_metrics(queue_stats)
    except:
        pass

    try:
        # Update storage metrics
        config = get_config()
        if config.assets_dir.exists():
            stat = shutil.disk_usage(config.assets_dir)
            free_gb = stat.free / (1024 ** 3)
            used_percent = (stat.used / stat.total) * 100
            update_storage_metrics(free_gb, used_percent)
    except:
        pass

    # Generate metrics in Prometheus format
    metrics = generate_latest()

    return Response(content=metrics, media_type=CONTENT_TYPE_LATEST)
