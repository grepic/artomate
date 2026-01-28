"""Simplified product definitions for getting started - Wall Art category."""

from typing import TypedDict, List

class SimplePrintArea(TypedDict):
    """Simple print area specification."""
    width: int
    height: int
    name: str  # Human-readable name like "8x10" or "12x16"

class SimpleProduct(TypedDict):
    """Simplified product for easy start."""
    product_id: str  # Internal ID like "poster_matte_vertical"
    name: str  # Display name
    blueprint_id: int  # Printify blueprint ID
    provider_id: int  # Printify provider ID
    category: str  # "wall_art", "apparel", etc.
    coverage_type: str  # "full" or "transparent"
    print_areas: List[SimplePrintArea]
    dpi: int
    notes: str


# ============================================================================
# WALL ART - STARTER PRODUCTS
# ============================================================================

STARTER_WALL_ART: dict[str, SimpleProduct] = {
    "poster_matte_vertical": {
        "product_id": "poster_matte_vertical",
        "name": "Matte Vertical Poster",
        "blueprint_id": 282,
        "provider_id": 99,
        "category": "wall_art",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Perfect for calendar - vertical orientation",
        "print_areas": [
            {"width": 2400, "height": 3000, "name": "8x10"},
            {"width": 3000, "height": 3000, "name": "10x10"},
            {"width": 3300, "height": 4200, "name": "11x14"},
            {"width": 3600, "height": 4800, "name": "12x16"},
            {"width": 3600, "height": 5400, "name": "12x18"},
            {"width": 4800, "height": 6000, "name": "16x20"},
            {"width": 5400, "height": 7200, "name": "18x24"},
            {"width": 7200, "height": 10800, "name": "24x36"},
        ],
    },
    "canvas_print": {
        "product_id": "canvas_print",
        "name": "Canvas Print",
        "blueprint_id": 184,
        "provider_id": 99,
        "category": "wall_art",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Gallery wrapped canvas",
        "print_areas": [
            {"width": 2400, "height": 2400, "name": "8x8 Square"},
            {"width": 3000, "height": 3000, "name": "10x10 Square"},
            {"width": 3600, "height": 3600, "name": "12x12 Square"},
            {"width": 2400, "height": 3000, "name": "8x10 Vertical"},
            {"width": 3600, "height": 4800, "name": "12x16 Vertical"},
            {"width": 4800, "height": 4800, "name": "16x16 Square"},
            {"width": 4800, "height": 6000, "name": "16x20 Vertical"},
            {"width": 5400, "height": 7200, "name": "18x24 Vertical"},
            {"width": 7200, "height": 10800, "name": "24x36 Vertical"},
        ],
    },
    "framed_poster_vertical": {
        "product_id": "framed_poster_vertical",
        "name": "Framed Vertical Poster",
        "blueprint_id": 540,
        "provider_id": 99,
        "category": "wall_art",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Poster with black or white frame",
        "print_areas": [
            {"width": 3000, "height": 3000, "name": "10x10"},
            {"width": 3600, "height": 4800, "name": "12x16"},
            {"width": 4800, "height": 6000, "name": "16x20"},
            {"width": 5400, "height": 7200, "name": "18x24"},
        ],
    },
}


def get_starter_products() -> dict[str, SimpleProduct]:
    """Get all starter products for wall art.
    
    Returns:
        Dict of product_id -> SimpleProduct
    """
    return STARTER_WALL_ART


def get_product(product_id: str) -> SimpleProduct:
    """Get specific product by ID.
    
    Args:
        product_id: Product ID (e.g., "poster_matte_vertical")
        
    Returns:
        Product specification
        
    Raises:
        KeyError: If product not found
    """
    return STARTER_WALL_ART[product_id]


def list_products() -> List[tuple[str, str, int]]:
    """List all available starter products.
    
    Returns:
        List of tuples: (product_id, name, number_of_sizes)
    """
    return [
        (
            prod["product_id"],
            prod["name"],
            len(prod["print_areas"]),
        )
        for prod in STARTER_WALL_ART.values()
    ]
