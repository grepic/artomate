"""Stock platform integration clients."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class StockPlatformClient(ABC):
    """Base class for stock platform clients."""

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize client with credentials."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform."""
        pass

    @abstractmethod
    def upload_image(
        self,
        image_path: Path,
        title: str,
        description: str,
        keywords: List[str],
        categories: Optional[List[str]] = None,
    ) -> Dict:
        """Upload an image to the platform."""
        pass

    @abstractmethod
    def get_submission_status(self, submission_id: str) -> Dict:
        """Get the status of a submission."""
        pass

    @abstractmethod
    def get_analytics(self, submission_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Get analytics for a submission."""
        pass


class ShutterstockClient(StockPlatformClient):
    """Shutterstock API client."""

    BASE_URL = "https://api.shutterstock.com/v2"

    def authenticate(self) -> bool:
        """Authenticate with Shutterstock."""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = self.session.get(f"{self.BASE_URL}/user", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Shutterstock authentication failed: {e}")
            return False

    def upload_image(
        self,
        image_path: Path,
        title: str,
        description: str,
        keywords: List[str],
        categories: Optional[List[str]] = None,
    ) -> Dict:
        """Upload an image to Shutterstock."""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}

            # Step 1: Upload image
            with open(image_path, "rb") as f:
                files = {"file": f}
                response = self.session.post(
                    f"{self.BASE_URL}/contributors/images",
                    headers=headers,
                    files=files,
                    timeout=60,
                )
                response.raise_for_status()
                upload_data = response.json()

            image_id = upload_data["id"]

            # Step 2: Add metadata
            metadata = {
                "title": title,
                "description": description,
                "keywords": keywords[:50],  # Max 50 keywords
                "categories": categories or [],
            }

            response = self.session.put(
                f"{self.BASE_URL}/contributors/images/{image_id}",
                headers=headers,
                json=metadata,
                timeout=30,
            )
            response.raise_for_status()

            return {
                "success": True,
                "submission_id": image_id,
                "platform_url": f"https://submit.shutterstock.com/edit?type=photo&id={image_id}",
                "status": "pending_review",
            }

        except Exception as e:
            logger.error(f"Shutterstock upload failed: {e}")
            return {"success": False, "error": str(e)}

    def get_submission_status(self, submission_id: str) -> Dict:
        """Get submission status."""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = self.session.get(
                f"{self.BASE_URL}/contributors/images/{submission_id}",
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "status": data.get("status", "unknown"),
                "submission_id": submission_id,
                "approved": data.get("is_approved", False),
                "live_url": data.get("url"),
            }

        except Exception as e:
            logger.error(f"Failed to get Shutterstock status: {e}")
            return {"status": "error", "error": str(e)}

    def get_analytics(self, submission_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Get analytics for submission."""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            params = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            }

            response = self.session.get(
                f"{self.BASE_URL}/contributors/images/{submission_id}/downloads",
                headers=headers,
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "downloads": data.get("total_count", 0),
                "earnings": data.get("total_earnings", 0.0),
                "views": data.get("views", 0),
            }

        except Exception as e:
            logger.error(f"Failed to get Shutterstock analytics: {e}")
            return {"error": str(e)}


class AdobeStockClient(StockPlatformClient):
    """Adobe Stock API client."""

    BASE_URL = "https://stock.adobe.io/Rest"

    def authenticate(self) -> bool:
        """Authenticate with Adobe Stock."""
        # Adobe uses OAuth 2.0 - this is a simplified version
        return bool(self.api_key)

    def upload_image(
        self,
        image_path: Path,
        title: str,
        description: str,
        keywords: List[str],
        categories: Optional[List[str]] = None,
    ) -> Dict:
        """Upload image to Adobe Stock."""
        # Adobe Stock requires OAuth and uses a more complex upload process
        logger.info("Adobe Stock upload - requires OAuth setup")
        return {
            "success": False,
            "error": "Adobe Stock requires OAuth authentication setup",
            "note": "Please configure OAuth credentials in platform settings",
        }

    def get_submission_status(self, submission_id: str) -> Dict:
        """Get submission status."""
        return {"status": "pending_oauth_setup"}

    def get_analytics(self, submission_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Get analytics."""
        return {"error": "OAuth setup required"}


class UnsplashClient(StockPlatformClient):
    """Unsplash API client."""

    BASE_URL = "https://api.unsplash.com"

    def authenticate(self) -> bool:
        """Authenticate with Unsplash."""
        try:
            headers = {"Authorization": f"Client-ID {self.api_key}"}
            response = self.session.get(f"{self.BASE_URL}/me", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Unsplash authentication failed: {e}")
            return False

    def upload_image(
        self,
        image_path: Path,
        title: str,
        description: str,
        keywords: List[str],
        categories: Optional[List[str]] = None,
    ) -> Dict:
        """Upload image to Unsplash."""
        try:
            headers = {"Authorization": f"Client-ID {self.api_key}"}

            with open(image_path, "rb") as f:
                files = {"photo": f}
                data = {
                    "description": description,
                    "location": "",
                    "exif": {},
                }

                response = self.session.post(
                    f"{self.BASE_URL}/photos",
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=60,
                )
                response.raise_for_status()
                result = response.json()

            return {
                "success": True,
                "submission_id": result["id"],
                "platform_url": result["links"]["html"],
                "status": "live",
            }

        except Exception as e:
            logger.error(f"Unsplash upload failed: {e}")
            return {"success": False, "error": str(e)}

    def get_submission_status(self, submission_id: str) -> Dict:
        """Get submission status."""
        try:
            headers = {"Authorization": f"Client-ID {self.api_key}"}
            response = self.session.get(
                f"{self.BASE_URL}/photos/{submission_id}",
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "status": "live",
                "submission_id": submission_id,
                "live_url": data["links"]["html"],
                "downloads": data.get("downloads", 0),
            }

        except Exception as e:
            logger.error(f"Failed to get Unsplash status: {e}")
            return {"status": "error", "error": str(e)}

    def get_analytics(self, submission_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Get analytics."""
        try:
            headers = {"Authorization": f"Client-ID {self.api_key}"}
            response = self.session.get(
                f"{self.BASE_URL}/photos/{submission_id}/statistics",
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "downloads": data.get("downloads", {}).get("total", 0),
                "views": data.get("views", {}).get("total", 0),
                "likes": data.get("likes", {}).get("total", 0),
            }

        except Exception as e:
            logger.error(f"Failed to get Unsplash analytics: {e}")
            return {"error": str(e)}


class PexelsClient(StockPlatformClient):
    """Pexels API client."""

    BASE_URL = "https://api.pexels.com/v1"

    def authenticate(self) -> bool:
        """Authenticate with Pexels."""
        return bool(self.api_key)

    def upload_image(
        self,
        image_path: Path,
        title: str,
        description: str,
        keywords: List[str],
        categories: Optional[List[str]] = None,
    ) -> Dict:
        """Upload image to Pexels."""
        # Pexels doesn't have a public upload API - requires manual submission
        return {
            "success": False,
            "error": "Pexels requires manual upload through their website",
            "note": "Visit https://www.pexels.com/upload to upload images",
        }

    def get_submission_status(self, submission_id: str) -> Dict:
        """Get submission status."""
        return {"status": "manual_upload_required"}

    def get_analytics(self, submission_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Get analytics."""
        return {"error": "Manual upload platform"}


# Platform client factory
PLATFORM_CLIENTS = {
    "shutterstock": ShutterstockClient,
    "adobe_stock": AdobeStockClient,
    "unsplash": UnsplashClient,
    "pexels": PexelsClient,
}


def get_platform_client(platform_name: str, api_key: str = None, api_secret: str = None) -> StockPlatformClient:
    """Get appropriate client for platform."""
    client_class = PLATFORM_CLIENTS.get(platform_name.lower())
    if not client_class:
        raise ValueError(f"Unknown platform: {platform_name}")

    return client_class(api_key=api_key, api_secret=api_secret)
