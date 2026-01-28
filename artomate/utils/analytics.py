"""Analytics and cost tracking module."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, func
from sqlalchemy.orm import Session
from loguru import logger

from artomate.db.base import Base


class CostType(str, Enum):
    """Types of costs."""
    IMAGE_GENERATION = "image_generation"
    API_CALL = "api_call"
    STORAGE = "storage"
    PROCESSING = "processing"


class CostRecord(Base):
    """Model for cost tracking."""
    
    __tablename__ = "cost_records"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, nullable=True, index=True)
    cost_type = Column(String(50), nullable=False)
    service = Column(String(100), nullable=False)  # openai, printify, etc.
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<CostRecord(id={self.id}, service={self.service}, amount=${self.amount:.4f})>"


@dataclass
class CostSummary:
    """Summary of costs."""
    total_cost: float
    by_service: Dict[str, float]
    by_type: Dict[str, float]
    count: int
    period_start: datetime
    period_end: datetime


@dataclass
class JobStats:
    """Job statistics."""
    total_jobs: int
    completed: int
    failed: int
    in_progress: int
    success_rate: float
    avg_duration_seconds: float
    total_assets: int
    total_products: int


class CostTracker:
    """Track and analyze costs."""
    
    def __init__(self, db: Session):
        """
        Initialize cost tracker.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def record_cost(
        self,
        cost_type: CostType,
        service: str,
        amount: float,
        job_id: Optional[int] = None,
        details: Optional[Dict] = None
    ):
        """
        Record a cost.
        
        Args:
            cost_type: Type of cost
            service: Service name (openai, printify, etc.)
            amount: Cost amount in USD
            job_id: Related job ID
            details: Additional details
        """
        cost = CostRecord(
            job_id=job_id,
            cost_type=cost_type.value,
            service=service,
            amount=amount,
            currency="USD",
            details=details or {}
        )
        
        self.db.add(cost)
        self.db.commit()
        
        logger.info(
            f"Cost recorded: {service}",
            cost_type=cost_type.value,
            amount=amount,
            job_id=job_id
        )
    
    def get_costs_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        job_id: Optional[int] = None
    ) -> CostSummary:
        """
        Get cost summary for a period.
        
        Args:
            start_date: Start date (default: 30 days ago)
            end_date: End date (default: now)
            job_id: Filter by job ID
            
        Returns:
            CostSummary
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        query = self.db.query(CostRecord).filter(
            CostRecord.created_at >= start_date,
            CostRecord.created_at <= end_date
        )
        
        if job_id:
            query = query.filter(CostRecord.job_id == job_id)
        
        costs = query.all()
        
        # Calculate totals
        total_cost = sum(c.amount for c in costs)
        
        # Group by service
        by_service = {}
        for cost in costs:
            by_service[cost.service] = by_service.get(cost.service, 0) + cost.amount
        
        # Group by type
        by_type = {}
        for cost in costs:
            by_type[cost.cost_type] = by_type.get(cost.cost_type, 0) + cost.amount
        
        return CostSummary(
            total_cost=total_cost,
            by_service=by_service,
            by_type=by_type,
            count=len(costs),
            period_start=start_date,
            period_end=end_date
        )
    
    def get_daily_costs(
        self,
        days: int = 30
    ) -> List[Dict]:
        """
        Get daily cost breakdown.
        
        Args:
            days: Number of days to retrieve
            
        Returns:
            List of daily cost totals
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query with date grouping
        results = self.db.query(
            func.date(CostRecord.created_at).label('date'),
            func.sum(CostRecord.amount).label('total')
        ).filter(
            CostRecord.created_at >= start_date
        ).group_by(
            func.date(CostRecord.created_at)
        ).order_by(
            func.date(CostRecord.created_at)
        ).all()
        
        return [
            {
                "date": result.date.isoformat(),
                "total_cost": float(result.total)
            }
            for result in results
        ]
    
    def estimate_job_cost(
        self,
        num_images: int = 1,
        image_provider: str = "openai",
        image_quality: str = "hd",
        num_products: int = 1
    ) -> Dict:
        """
        Estimate cost for a job.
        
        Args:
            num_images: Number of images to generate
            image_provider: Image generation provider
            image_quality: Image quality
            num_products: Number of products to create
            
        Returns:
            Cost estimate breakdown
        """
        costs = {}
        
        # Image generation costs (OpenAI DALL-E 3)
        if image_provider == "openai":
            if image_quality == "hd":
                cost_per_image = 0.080  # $0.080 for 1024x1024 HD
            else:
                cost_per_image = 0.040  # $0.040 for 1024x1024 standard
            
            costs["image_generation"] = num_images * cost_per_image
        
        # Printify costs (varies by product, estimate $0.01 per API call)
        costs["printify_api"] = num_products * 0.01
        
        # Total
        costs["total_estimated"] = sum(costs.values())
        
        return costs


class AnalyticsCollector:
    """Collect and analyze system analytics."""
    
    def __init__(self, db: Session):
        """
        Initialize analytics collector.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_job_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> JobStats:
        """
        Get job statistics.
        
        Args:
            start_date: Start date (default: 30 days ago)
            end_date: End date (default: now)
            
        Returns:
            JobStats
        """
        from artomate.db.models import Job, JobStatus
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        query = self.db.query(Job).filter(
            Job.created_at >= start_date,
            Job.created_at <= end_date
        )
        
        jobs = query.all()
        
        total_jobs = len(jobs)
        completed = sum(1 for j in jobs if j.status == JobStatus.COMPLETED)
        failed = sum(1 for j in jobs if j.status == JobStatus.FAILED)
        in_progress = sum(1 for j in jobs if j.status == JobStatus.PROCESSING)
        
        success_rate = (completed / total_jobs * 100) if total_jobs > 0 else 0
        
        # Calculate average duration for completed jobs
        durations = []
        for job in jobs:
            if job.status == JobStatus.COMPLETED and job.completed_at:
                duration = (job.completed_at - job.created_at).total_seconds()
                durations.append(duration)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Count assets and products
        total_assets = sum(len(j.assets) for j in jobs if hasattr(j, 'assets'))
        total_products = sum(len(j.products) for j in jobs if hasattr(j, 'products'))
        
        return JobStats(
            total_jobs=total_jobs,
            completed=completed,
            failed=failed,
            in_progress=in_progress,
            success_rate=success_rate,
            avg_duration_seconds=avg_duration,
            total_assets=total_assets,
            total_products=total_products
        )
    
    def get_dashboard_data(self) -> Dict:
        """
        Get comprehensive dashboard data.
        
        Returns:
            Dictionary with dashboard metrics
        """
        cost_tracker = CostTracker(self.db)
        
        # Last 30 days
        cost_summary = cost_tracker.get_costs_summary()
        job_stats = self.get_job_stats()
        daily_costs = cost_tracker.get_daily_costs(days=30)
        
        return {
            "period": {
                "start": cost_summary.period_start.isoformat(),
                "end": cost_summary.period_end.isoformat()
            },
            "costs": {
                "total": cost_summary.total_cost,
                "by_service": cost_summary.by_service,
                "by_type": cost_summary.by_type,
                "daily": daily_costs
            },
            "jobs": {
                "total": job_stats.total_jobs,
                "completed": job_stats.completed,
                "failed": job_stats.failed,
                "in_progress": job_stats.in_progress,
                "success_rate": job_stats.success_rate,
                "avg_duration_seconds": job_stats.avg_duration_seconds
            },
            "production": {
                "total_assets": job_stats.total_assets,
                "total_products": job_stats.total_products,
                "assets_per_job": job_stats.total_assets / job_stats.total_jobs if job_stats.total_jobs > 0 else 0,
                "products_per_job": job_stats.total_products / job_stats.total_jobs if job_stats.total_jobs > 0 else 0
            }
        }


# OpenAI cost tracking helper
class OpenAICostCalculator:
    """Calculate OpenAI API costs."""
    
    # Pricing as of 2024 (USD)
    PRICES = {
        "gpt-4": {
            "input": 0.03 / 1000,  # per token
            "output": 0.06 / 1000
        },
        "gpt-3.5-turbo": {
            "input": 0.0015 / 1000,
            "output": 0.002 / 1000
        },
        "dall-e-3": {
            "1024x1024-hd": 0.080,
            "1024x1024-standard": 0.040,
            "1024x1792-hd": 0.120,
            "1792x1024-hd": 0.120
        }
    }
    
    @classmethod
    def calculate_text_cost(
        cls,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost for text generation."""
        if model not in cls.PRICES:
            return 0.0
        
        prices = cls.PRICES[model]
        return (
            input_tokens * prices["input"] +
            output_tokens * prices["output"]
        )
    
    @classmethod
    def calculate_image_cost(
        cls,
        size: str,
        quality: str = "hd"
    ) -> float:
        """Calculate cost for image generation."""
        key = f"{size}-{quality}"
        return cls.PRICES["dall-e-3"].get(key, 0.0)


# Usage examples:
#
# 1. Track cost:
#    tracker = CostTracker(db_session)
#    tracker.record_cost(
#        cost_type=CostType.IMAGE_GENERATION,
#        service="openai",
#        amount=0.080,
#        job_id=123
#    )
#
# 2. Get cost summary:
#    summary = tracker.get_costs_summary()
#    print(f"Total: ${summary.total_cost:.2f}")
#
# 3. Get dashboard data:
#    analytics = AnalyticsCollector(db_session)
#    data = analytics.get_dashboard_data()
#
# 4. Estimate job cost:
#    estimate = tracker.estimate_job_cost(num_images=5, num_products=3)
#    print(f"Estimated: ${estimate['total_estimated']:.2f}")
