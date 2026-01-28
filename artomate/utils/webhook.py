"""Webhook delivery system with retries and persistence."""

import json
import hmac
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

import httpx
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from loguru import logger

from artomate.db.base import Base
from artomate.utils.retry import retry_with_backoff


class WebhookStatus(str, Enum):
    """Webhook delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class WebhookEvent(Base):
    """Model for webhook events."""
    
    __tablename__ = "webhook_events"
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(255), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    target_url = Column(String(1024), nullable=False)
    status = Column(String(50), default=WebhookStatus.PENDING)
    attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, nullable=True)
    response_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)


class WebhookManager:
    """Manager for sending webhooks with retry logic."""
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        Initialize webhook manager.
        
        Args:
            secret_key: Secret key for HMAC signatures
            max_retries: Maximum retry attempts
            timeout: Request timeout in seconds
        """
        self.secret_key = secret_key
        self.max_retries = max_retries
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    def _generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for webhook payload."""
        if not self.secret_key:
            return ""
        
        signature = hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    @retry_with_backoff(max_retries=3, base_delay=5.0)
    async def send_webhook(
        self,
        url: str,
        event_type: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send webhook to URL.
        
        Args:
            url: Target URL
            event_type: Type of event
            payload: Event payload
            headers: Additional headers
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare payload
            webhook_payload = {
                "event": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": payload
            }
            
            payload_str = json.dumps(webhook_payload)
            
            # Prepare headers
            request_headers = {
                "Content-Type": "application/json",
                "User-Agent": "Artomate-Webhook/1.0",
                "X-Webhook-Event": event_type,
                **(headers or {})
            }
            
            # Add signature if secret key is configured
            if self.secret_key:
                signature = self._generate_signature(payload_str)
                request_headers["X-Webhook-Signature"] = signature
            
            # Send request
            response = await self.client.post(
                url,
                content=payload_str,
                headers=request_headers
            )
            
            # Check response
            response.raise_for_status()
            
            logger.info(
                f"Webhook delivered successfully",
                event_type=event_type,
                url=url,
                status_code=response.status_code
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f"Webhook delivery failed",
                event_type=event_type,
                url=url,
                error=str(e)
            )
            raise
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class WebhookDispatcher:
    """Dispatch webhooks with persistence and retry."""
    
    def __init__(self, db, webhook_manager: WebhookManager):
        """
        Initialize webhook dispatcher.
        
        Args:
            db: Database session
            webhook_manager: WebhookManager instance
        """
        self.db = db
        self.manager = webhook_manager
    
    async def dispatch(
        self,
        event_type: str,
        payload: Dict[str, Any],
        target_urls: List[str]
    ):
        """
        Dispatch webhook to multiple URLs.
        
        Args:
            event_type: Type of event
            payload: Event payload
            target_urls: List of target URLs
        """
        for url in target_urls:
            # Create webhook event record
            event = WebhookEvent(
                event_type=event_type,
                payload=payload,
                target_url=url,
                status=WebhookStatus.PENDING
            )
            self.db.add(event)
            self.db.commit()
            
            # Try to send
            try:
                await self.manager.send_webhook(url, event_type, payload)
                
                # Update status
                event.status = WebhookStatus.DELIVERED
                event.delivered_at = datetime.utcnow()
                event.attempts += 1
                event.last_attempt_at = datetime.utcnow()
                
            except Exception as e:
                event.status = WebhookStatus.FAILED
                event.error_message = str(e)
                event.attempts += 1
                event.last_attempt_at = datetime.utcnow()
            
            self.db.commit()
    
    async def retry_failed(self, limit: int = 100):
        """Retry failed webhook deliveries."""
        failed_events = self.db.query(WebhookEvent).filter(
            WebhookEvent.status == WebhookStatus.FAILED,
            WebhookEvent.attempts < self.manager.max_retries
        ).limit(limit).all()
        
        logger.info(f"Retrying {len(failed_events)} failed webhooks")
        
        for event in failed_events:
            try:
                event.status = WebhookStatus.RETRYING
                self.db.commit()
                
                await self.manager.send_webhook(
                    event.target_url,
                    event.event_type,
                    event.payload
                )
                
                event.status = WebhookStatus.DELIVERED
                event.delivered_at = datetime.utcnow()
                
            except Exception as e:
                event.status = WebhookStatus.FAILED
                event.error_message = str(e)
            
            event.attempts += 1
            event.last_attempt_at = datetime.utcnow()
            self.db.commit()


# N8N Integration helpers

class N8NWebhook:
    """Helper for sending webhooks to n8n."""
    
    def __init__(self, webhook_url: str, api_key: Optional[str] = None):
        """
        Initialize n8n webhook.
        
        Args:
            webhook_url: n8n webhook URL
            api_key: Optional n8n API key
        """
        self.webhook_url = webhook_url
        self.api_key = api_key
        self.manager = WebhookManager()
    
    async def trigger_workflow(
        self,
        workflow_name: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Trigger n8n workflow.
        
        Args:
            workflow_name: Name of the workflow
            data: Data to pass to workflow
            
        Returns:
            True if successful
        """
        headers = {}
        if self.api_key:
            headers["X-N8N-API-KEY"] = self.api_key
        
        return await self.manager.send_webhook(
            self.webhook_url,
            workflow_name,
            data,
            headers=headers
        )
    
    async def notify_job_completed(
        self,
        job_id: int,
        assets_count: int,
        products_count: int
    ):
        """Notify n8n that a job completed."""
        return await self.trigger_workflow(
            "job_completed",
            {
                "job_id": job_id,
                "assets_count": assets_count,
                "products_count": products_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
    
    async def notify_job_failed(self, job_id: int, error: str):
        """Notify n8n that a job failed."""
        return await self.trigger_workflow(
            "job_failed",
            {
                "job_id": job_id,
                "error": error,
                "failed_at": datetime.utcnow().isoformat()
            }
        )


# Usage examples:
#
# 1. Send simple webhook:
#    manager = WebhookManager(secret_key="your-secret")
#    await manager.send_webhook(
#        url="https://example.com/webhook",
#        event_type="job.completed",
#        payload={"job_id": 123}
#    )
#
# 2. Use webhook dispatcher with persistence:
#    dispatcher = WebhookDispatcher(db_session, webhook_manager)
#    await dispatcher.dispatch(
#        event_type="product.created",
#        payload={"product_id": 456},
#        target_urls=["https://example.com/webhook"]
#    )
#
# 3. n8n integration:
#    n8n = N8NWebhook("http://localhost:5678/webhook/artomate")
#    await n8n.notify_job_completed(job_id=123, assets_count=5, products_count=3)
