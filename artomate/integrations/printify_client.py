"""Printify API client (unofficial wrapper)."""

from pathlib import Path
from typing import Any, Optional

import requests
from loguru import logger

from artomate.core.config import Config, get_config


class PrintifyClient:
    """Printify API client.

    API Documentation: https://developers.printify.com/
    """

    BASE_URL = "https://api.printify.com/v1"

    def __init__(self, api_token: Optional[str] = None, shop_id: Optional[int] = None):
        """Initialize Printify client.

        Args:
            api_token: Printify API token
            shop_id: Printify shop ID
        """
        config = get_config()

        self.api_token = api_token or config.printify_api_token
        self.shop_id = shop_id or config.printify_shop_id

        if not self.api_token:
            raise ValueError("Printify API token not configured")

        if not self.shop_id:
            raise ValueError("Printify shop ID not configured")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            }
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Make API request.

        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            data: JSON data for POST/PUT
            params: Query parameters

        Returns:
            API response as dict

        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            return response.json() if response.content else {}

        except requests.HTTPError as e:
            logger.error(f"Printify API error: {e.response.status_code} - {e.response.text}")
            raise

    # ========================================================================
    # Shops
    # ========================================================================

    def get_shops(self) -> list[dict]:
        """Get list of shops.

        Returns:
            List of shop dicts
        """
        return self._request("GET", "/shops.json")

    # ========================================================================
    # Catalog (Blueprints & Print Providers)
    # ========================================================================

    def get_catalog(self) -> dict[str, Any]:
        """Get full product catalog.

        Returns:
            Catalog data with blueprints and providers
        """
        return self._request("GET", "/catalog/blueprints.json")

    def get_blueprint(self, blueprint_id: int) -> dict:
        """Get blueprint details.

        Args:
            blueprint_id: Blueprint ID

        Returns:
            Blueprint data
        """
        return self._request("GET", f"/catalog/blueprints/{blueprint_id}.json")

    def get_blueprint_providers(self, blueprint_id: int) -> list[dict]:
        """Get print providers for a blueprint.

        Args:
            blueprint_id: Blueprint ID

        Returns:
            List of provider dicts
        """
        return self._request("GET", f"/catalog/blueprints/{blueprint_id}/print_providers.json")

    def get_blueprint_variants(
        self,
        blueprint_id: int,
        print_provider_id: int,
    ) -> dict:
        """Get variants for a blueprint and provider.

        Args:
            blueprint_id: Blueprint ID
            print_provider_id: Print provider ID

        Returns:
            Variants data with print areas
        """
        return self._request(
            "GET",
            f"/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json",
        )

    # ========================================================================
    # Images
    # ========================================================================

    def upload_image(
        self,
        image_path: Path | str,
        file_name: Optional[str] = None,
    ) -> dict:
        """Upload image to Printify.

        Args:
            image_path: Path to image file
            file_name: Optional custom filename

        Returns:
            Upload response with image ID

        Raises:
            FileNotFoundError: If image file not found
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        file_name = file_name or image_path.name

        logger.info(f"Uploading image to Printify: {file_name}")

        # Printify expects base64 or URL
        # For simplicity, we'll use their upload endpoint
        with open(image_path, "rb") as f:
            files = {"file": (file_name, f, "image/png")}

            url = f"{self.BASE_URL}/uploads/images.json"

            response = self.session.post(
                url,
                files=files,
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=60,
            )

            response.raise_for_status()

            result = response.json()

            logger.info(f"✓ Uploaded image: ID {result.get('id')}")

            return result

    # ========================================================================
    # Products
    # ========================================================================

    def create_product(
        self,
        title: str,
        description: str,
        blueprint_id: int,
        print_provider_id: int,
        variants: list[dict],
        print_areas: list[dict],
        tags: Optional[list[str]] = None,
    ) -> dict:
        """Create a new product.

        Args:
            title: Product title
            description: Product description
            blueprint_id: Blueprint ID
            print_provider_id: Print provider ID
            variants: List of variant configurations
            print_areas: List of print area configurations
            tags: Optional product tags

        Returns:
            Created product data

        Example:
            ```python
            client.create_product(
                title="Cat T-Shirt",
                description="Beautiful cat design",
                blueprint_id=3,
                print_provider_id=99,
                variants=[
                    {"id": 12345, "price": 2999, "is_enabled": True},
                ],
                print_areas=[
                    {
                        "variant_ids": [12345],
                        "placeholders": [
                            {"position": "front", "images": [{"id": "abc123"}]}
                        ]
                    }
                ],
                tags=["cat", "minimalist"]
            )
            ```
        """
        data = {
            "title": title,
            "description": description,
            "blueprint_id": blueprint_id,
            "print_provider_id": print_provider_id,
            "variants": variants,
            "print_areas": print_areas,
        }

        if tags:
            data["tags"] = tags

        logger.info(f"Creating Printify product: '{title}'")

        result = self._request("POST", f"/shops/{self.shop_id}/products.json", data=data)

        logger.info(f"✓ Created product: ID {result.get('id')}")

        return result

    def get_product(self, product_id: str) -> dict:
        """Get product details.

        Args:
            product_id: Product ID

        Returns:
            Product data
        """
        return self._request("GET", f"/shops/{self.shop_id}/products/{product_id}.json")

    def update_product(
        self,
        product_id: str,
        **updates: Any,
    ) -> dict:
        """Update product.

        Args:
            product_id: Product ID
            **updates: Fields to update

        Returns:
            Updated product data
        """
        return self._request(
            "PUT",
            f"/shops/{self.shop_id}/products/{product_id}.json",
            data=updates,
        )

    def delete_product(self, product_id: str) -> bool:
        """Delete product.

        Args:
            product_id: Product ID

        Returns:
            True if deleted
        """
        self._request("DELETE", f"/shops/{self.shop_id}/products/{product_id}.json")
        logger.info(f"✓ Deleted product: {product_id}")
        return True

    def publish_product(
        self,
        product_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> dict:
        """Publish product to connected sales channel (e.g., Etsy).

        Args:
            product_id: Product ID
            title: Optional override title
            description: Optional override description
            tags: Optional tags

        Returns:
            Publishing response
        """
        data = {}

        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags

        logger.info(f"Publishing product {product_id}")

        result = self._request(
            "POST",
            f"/shops/{self.shop_id}/products/{product_id}/publish.json",
            data=data if data else None,
        )

        logger.info(f"✓ Published product {product_id}")

        return result

    def unpublish_product(self, product_id: str) -> dict:
        """Unpublish product from sales channel.

        Args:
            product_id: Product ID

        Returns:
            Unpublishing response
        """
        result = self._request(
            "POST",
            f"/shops/{self.shop_id}/products/{product_id}/unpublish.json",
        )

        logger.info(f"✓ Unpublished product {product_id}")

        return result

    # ========================================================================
    # Orders (read-only for now)
    # ========================================================================

    def get_orders(
        self,
        limit: int = 100,
        page: int = 1,
    ) -> dict:
        """Get orders.

        Args:
            limit: Results per page
            page: Page number

        Returns:
            Orders data
        """
        params = {"limit": limit, "page": page}

        return self._request("GET", f"/shops/{self.shop_id}/orders.json", params=params)

    def get_order(self, order_id: str) -> dict:
        """Get order details.

        Args:
            order_id: Order ID

        Returns:
            Order data
        """
        return self._request("GET", f"/shops/{self.shop_id}/orders/{order_id}.json")


# ============================================================================
# Helper Functions
# ============================================================================


def get_printify_client() -> PrintifyClient:
    """Get configured Printify client instance.

    Returns:
        PrintifyClient instance
    """
    return PrintifyClient()
