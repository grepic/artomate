"""Etsy API client (unofficial wrapper)."""

from typing import Any, Optional

import requests
from loguru import logger

from artomate.core.config import Config, get_config


class EtsyClient:
    """Etsy API v3 client.

    API Documentation: https://developers.etsy.com/documentation
    """

    BASE_URL = "https://openapi.etsy.com/v3/application"

    def __init__(
        self,
        api_key: Optional[str] = None,
        shop_id: Optional[int] = None,
        access_token: Optional[str] = None,
    ):
        """Initialize Etsy client.

        Args:
            api_key: Etsy API key
            shop_id: Etsy shop ID
            access_token: OAuth access token
        """
        config = get_config()

        self.api_key = api_key or config.etsy_api_key
        self.shop_id = shop_id or config.etsy_shop_id
        self.access_token = access_token

        if not self.api_key:
            raise ValueError("Etsy API key not configured")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
            }
        )

        if self.access_token:
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})

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
            logger.error(f"Etsy API error: {e.response.status_code} - {e.response.text}")
            raise

    # ========================================================================
    # Shops
    # ========================================================================

    def get_shop(self, shop_id: Optional[int] = None) -> dict:
        """Get shop details.

        Args:
            shop_id: Shop ID (uses configured shop_id if not provided)

        Returns:
            Shop data
        """
        shop_id = shop_id or self.shop_id
        return self._request("GET", f"/shops/{shop_id}")

    # ========================================================================
    # Listings
    # ========================================================================

    def create_listing(
        self,
        title: str,
        description: str,
        price: float,
        quantity: int = 999,
        taxonomy_id: int = 1,
        who_made: str = "i_did",
        when_made: str = "made_to_order",
        is_supply: bool = False,
        shipping_profile_id: Optional[int] = None,
        tags: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> dict:
        """Create a new listing.

        Args:
            title: Listing title (max 140 chars)
            description: Listing description
            price: Price in dollars
            quantity: Available quantity
            taxonomy_id: Etsy taxonomy/category ID
            who_made: Who made it ("i_did", "someone_else", "collective")
            when_made: When made ("made_to_order", "2020_2023", etc.)
            is_supply: Is this a supply/tool
            shipping_profile_id: Shipping profile ID
            tags: List of tags (max 13)
            **kwargs: Additional parameters

        Returns:
            Created listing data
        """
        if not self.shop_id:
            raise ValueError("Shop ID not configured")

        data = {
            "title": title[:140],
            "description": description,
            "price": price,
            "quantity": quantity,
            "taxonomy_id": taxonomy_id,
            "who_made": who_made,
            "when_made": when_made,
            "is_supply": is_supply,
        }

        if shipping_profile_id:
            data["shipping_profile_id"] = shipping_profile_id

        if tags:
            data["tags"] = tags[:13]  # Etsy limit

        data.update(kwargs)

        logger.info(f"Creating Etsy listing: '{title}'")

        result = self._request("POST", f"/shops/{self.shop_id}/listings", data=data)

        logger.info(f"✓ Created listing: {result.get('listing_id')}")

        return result

    def update_listing(
        self,
        listing_id: int,
        **updates: Any,
    ) -> dict:
        """Update listing.

        Args:
            listing_id: Listing ID
            **updates: Fields to update

        Returns:
            Updated listing data
        """
        return self._request(
            "PATCH",
            f"/shops/{self.shop_id}/listings/{listing_id}",
            data=updates,
        )

    def get_listing(self, listing_id: int) -> dict:
        """Get listing details.

        Args:
            listing_id: Listing ID

        Returns:
            Listing data
        """
        return self._request("GET", f"/listings/{listing_id}")

    def delete_listing(self, listing_id: int) -> bool:
        """Delete listing.

        Args:
            listing_id: Listing ID

        Returns:
            True if deleted
        """
        self._request("DELETE", f"/listings/{listing_id}")
        logger.info(f"✓ Deleted listing: {listing_id}")
        return True

    def upload_listing_image(
        self,
        listing_id: int,
        image_path: str,
        rank: int = 1,
    ) -> dict:
        """Upload image to listing.

        Args:
            listing_id: Listing ID
            image_path: Path to image file
            rank: Image rank (1 = primary)

        Returns:
            Upload response
        """
        url = f"{self.BASE_URL}/shops/{self.shop_id}/listings/{listing_id}/images"

        with open(image_path, "rb") as f:
            files = {"image": f}
            data = {"rank": rank}

            response = self.session.post(
                url,
                files=files,
                data=data,
                timeout=60,
            )

            response.raise_for_status()

            logger.info(f"✓ Uploaded image to listing {listing_id}")

            return response.json()

    # ========================================================================
    # Taxonomy (Categories)
    # ========================================================================

    def get_seller_taxonomy(self) -> list[dict]:
        """Get seller taxonomy (categories).

        Returns:
            List of taxonomy nodes
        """
        return self._request("GET", "/seller-taxonomy/nodes")

    def search_taxonomy(self, query: str) -> list[dict]:
        """Search for taxonomy by name.

        Args:
            query: Search query

        Returns:
            Matching taxonomy nodes
        """
        all_taxonomy = self.get_seller_taxonomy()

        # Simple search (can be enhanced)
        results = [
            node
            for node in all_taxonomy
            if query.lower() in node.get("name", "").lower()
        ]

        return results

    # ========================================================================
    # Shop Sections
    # ========================================================================

    def create_shop_section(self, title: str) -> dict:
        """Create shop section.

        Args:
            title: Section title

        Returns:
            Created section data
        """
        data = {"title": title}

        return self._request("POST", f"/shops/{self.shop_id}/sections", data=data)

    def get_shop_sections(self) -> list[dict]:
        """Get shop sections.

        Returns:
            List of sections
        """
        return self._request("GET", f"/shops/{self.shop_id}/sections")

    # ========================================================================
    # Stats
    # ========================================================================

    def get_shop_stats(self, shop_id: Optional[int] = None) -> dict:
        """Get shop statistics.

        Args:
            shop_id: Shop ID

        Returns:
            Shop stats
        """
        shop_id = shop_id or self.shop_id
        return self._request("GET", f"/shops/{shop_id}/stats")

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def find_taxonomy_for_niche(self, niche: str) -> Optional[int]:
        """Find best taxonomy ID for a niche.

        Args:
            niche: Niche category

        Returns:
            Taxonomy ID or None
        """
        # Map common niches to Etsy taxonomies
        niche_map = {
            "wall-art": 1,  # Art & Collectibles
            "apparel": 6,  # Clothing
            "home-decor": 4,  # Home & Living
            "stationery": 3,  # Paper & Party Supplies
            "accessories": 5,  # Accessories
        }

        # Try direct mapping
        if niche in niche_map:
            return niche_map[niche]

        # Try searching
        try:
            results = self.search_taxonomy(niche)
            if results:
                return results[0].get("id")
        except:
            pass

        # Default to Art
        return 1


# ============================================================================
# Helper Functions
# ============================================================================


def get_etsy_client() -> EtsyClient:
    """Get configured Etsy client instance.

    Returns:
        EtsyClient instance
    """
    return EtsyClient()
