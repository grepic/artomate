"""Feed export functionality (XML/CSV/JSON)."""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional
from xml.etree import ElementTree as ET

from loguru import logger

from artomate.core.config import Config, get_config
from artomate.db.database import get_db
from artomate.db.models import Job, MarketplaceListing, Product


FeedFormat = Literal["xml", "csv", "json"]


class FeedExporter:
    """Exports product/listing feeds in various formats."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize feed exporter.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self.db = get_db()

    def export_products(
        self,
        format: FeedFormat,
        output_path: Optional[Path] = None,
        filters: Optional[dict] = None,
    ) -> Path:
        """Export products feed.

        Args:
            format: Export format (xml, csv, json)
            output_path: Output file path (auto-generated if None)
            filters: Optional filters (e.g., {"niche": "wall-art"})

        Returns:
            Path to exported file
        """
        # Get products
        with self.db.session_scope() as session:
            query = session.query(Product).join(Job)

            # Apply filters
            if filters:
                if "niche" in filters:
                    query = query.filter(Job.niche == filters["niche"])
                if "style" in filters:
                    query = query.filter(Job.style == filters["style"])

            products = query.all()

            # Convert to dicts (detach from session)
            products_data = [self._product_to_dict(p) for p in products]

        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"products_{timestamp}.{format}"
            output_path = self.config.exports_dir / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Export based on format
        if format == "xml":
            self._export_products_xml(products_data, output_path)
        elif format == "csv":
            self._export_products_csv(products_data, output_path)
        elif format == "json":
            self._export_products_json(products_data, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"✓ Exported {len(products_data)} products to {output_path}")

        return output_path

    def export_listings(
        self,
        format: FeedFormat,
        marketplace: Optional[str] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Export marketplace listings feed.

        Args:
            format: Export format (xml, csv, json)
            marketplace: Optional marketplace filter (e.g., "etsy")
            output_path: Output file path

        Returns:
            Path to exported file
        """
        # Get listings
        with self.db.session_scope() as session:
            query = session.query(MarketplaceListing)

            if marketplace:
                query = query.filter(MarketplaceListing.marketplace == marketplace)

            listings = query.all()
            listings_data = [self._listing_to_dict(l) for l in listings]

        # Generate output path
        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            prefix = f"{marketplace}_" if marketplace else ""
            filename = f"{prefix}listings_{timestamp}.{format}"
            output_path = self.config.exports_dir / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Export
        if format == "xml":
            self._export_listings_xml(listings_data, output_path)
        elif format == "csv":
            self._export_listings_csv(listings_data, output_path)
        elif format == "json":
            self._export_listings_json(listings_data, output_path)

        logger.info(f"✓ Exported {len(listings_data)} listings to {output_path}")

        return output_path

    # ========================================================================
    # XML Export
    # ========================================================================

    def _export_products_xml(self, products: list[dict], output_path: Path) -> None:
        """Export products to XML."""
        root = ET.Element("products")
        root.set("count", str(len(products)))
        root.set("generated", datetime.utcnow().isoformat())

        for product in products:
            product_elem = ET.SubElement(root, "product")
            product_elem.set("id", str(product["id"]))

            for key, value in product.items():
                if key == "id":
                    continue
                if value is None:
                    continue

                elem = ET.SubElement(product_elem, key)

                if isinstance(value, (list, dict)):
                    elem.text = json.dumps(value)
                else:
                    elem.text = str(value)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(output_path, encoding="utf-8", xml_declaration=True)

    def _export_listings_xml(self, listings: list[dict], output_path: Path) -> None:
        """Export listings to XML."""
        root = ET.Element("listings")
        root.set("count", str(len(listings)))
        root.set("generated", datetime.utcnow().isoformat())

        for listing in listings:
            listing_elem = ET.SubElement(root, "listing")
            listing_elem.set("id", str(listing["id"]))

            for key, value in listing.items():
                if key == "id":
                    continue
                if value is None:
                    continue

                elem = ET.SubElement(listing_elem, key)

                if isinstance(value, (list, dict)):
                    elem.text = json.dumps(value)
                else:
                    elem.text = str(value)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(output_path, encoding="utf-8", xml_declaration=True)

    # ========================================================================
    # CSV Export
    # ========================================================================

    def _export_products_csv(self, products: list[dict], output_path: Path) -> None:
        """Export products to CSV."""
        if not products:
            return

        # Flatten nested fields
        flattened = [self._flatten_dict(p) for p in products]

        # Get all columns
        all_keys = set()
        for row in flattened:
            all_keys.update(row.keys())

        fieldnames = sorted(all_keys)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened)

    def _export_listings_csv(self, listings: list[dict], output_path: Path) -> None:
        """Export listings to CSV."""
        if not listings:
            return

        flattened = [self._flatten_dict(l) for l in listings]

        all_keys = set()
        for row in flattened:
            all_keys.update(row.keys())

        fieldnames = sorted(all_keys)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened)

    # ========================================================================
    # JSON Export
    # ========================================================================

    def _export_products_json(self, products: list[dict], output_path: Path) -> None:
        """Export products to JSON."""
        data = {
            "generated": datetime.utcnow().isoformat(),
            "count": len(products),
            "products": products,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _export_listings_json(self, listings: list[dict], output_path: Path) -> None:
        """Export listings to JSON."""
        data = {
            "generated": datetime.utcnow().isoformat(),
            "count": len(listings),
            "listings": listings,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _product_to_dict(self, product: Product) -> dict:
        """Convert Product to dict.

        Args:
            product: Product instance

        Returns:
            Product as dict
        """
        return {
            "id": product.id,
            "job_id": product.job_id,
            "title": product.title,
            "description": product.description,
            "tags": product.tags,
            "printify_product_id": product.printify_product_id,
            "printify_status": product.printify_status,
            "base_cost": float(product.base_cost) if product.base_cost else None,
            "selling_price": float(product.selling_price) if product.selling_price else None,
            "profit_margin": float(product.profit_margin) if product.profit_margin else None,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        }

    def _listing_to_dict(self, listing: MarketplaceListing) -> dict:
        """Convert MarketplaceListing to dict.

        Args:
            listing: Listing instance

        Returns:
            Listing as dict
        """
        return {
            "id": listing.id,
            "product_id": listing.product_id,
            "job_id": listing.job_id,
            "marketplace": listing.marketplace.value if listing.marketplace else None,
            "marketplace_listing_id": listing.marketplace_listing_id,
            "title": listing.title,
            "description": listing.description,
            "tags": listing.tags,
            "status": listing.status,
            "listing_url": listing.listing_url,
            "price": float(listing.price) if listing.price else None,
            "currency": listing.currency,
            "views_count": listing.views_count,
            "favorites_count": listing.favorites_count,
            "orders_count": listing.orders_count,
            "revenue": float(listing.revenue) if listing.revenue else None,
            "created_at": listing.created_at.isoformat() if listing.created_at else None,
        }

    def _flatten_dict(self, d: dict, parent_key: str = "", sep: str = "_") -> dict:
        """Flatten nested dict for CSV export.

        Args:
            d: Dict to flatten
            parent_key: Parent key prefix
            sep: Separator

        Returns:
            Flattened dict
        """
        items = []

        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to JSON strings
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))

        return dict(items)


# ============================================================================
# Helper Functions
# ============================================================================


def export_products(
    format: FeedFormat = "json",
    output_path: Optional[Path] = None,
    **filters,
) -> Path:
    """Export products feed.

    Args:
        format: Export format
        output_path: Output path
        **filters: Filter criteria

    Returns:
        Path to exported file
    """
    exporter = FeedExporter()
    return exporter.export_products(format, output_path, filters)


def export_listings(
    format: FeedFormat = "json",
    marketplace: Optional[str] = None,
    output_path: Optional[Path] = None,
) -> Path:
    """Export listings feed.

    Args:
        format: Export format
        marketplace: Marketplace filter
        output_path: Output path

    Returns:
        Path to exported file
    """
    exporter = FeedExporter()
    return exporter.export_listings(format, marketplace, output_path)
