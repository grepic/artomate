"""Comprehensive Printify product catalog with print specifications."""

from typing import Literal, TypedDict


CoverageType = Literal["transparent", "full", "centered"]


class PrintifyProductSpec(TypedDict):
    """Printify product specification."""

    blueprint_id: int
    provider_id: int
    print_area: dict[str, int]  # width, height in pixels
    name: str
    coverage_type: CoverageType
    dpi: int
    notes: str


# ============================================================================
# COMPREHENSIVE PRINTIFY PRODUCT CATALOG
# ============================================================================

PRINTIFY_PRODUCTS: dict[str, PrintifyProductSpec] = {
    # ========================================================================
    # APPAREL - Transparent Background
    # ========================================================================
    "tshirt_unisex": {
        "blueprint_id": 6,
        "provider_id": 99,
        "print_area": {"width": 4500, "height": 5400},
        "name": "Unisex Heavy Cotton Tee",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Classic t-shirt, centered print area",
    },
    "tshirt_premium": {
        "blueprint_id": 5,
        "provider_id": 99,
        "print_area": {"width": 4500, "height": 5400},
        "name": "Unisex Cotton Crew Tee",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Higher quality fabric",
    },
    "tshirt_womens": {
        "blueprint_id": 9,
        "provider_id": 99,
        "print_area": {"width": 4500, "height": 5400},
        "name": "Women's Favorite Tee",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Women's fitted cut",
    },
    "tshirt_kids": {
        "blueprint_id": 67,
        "provider_id": 99,
        "print_area": {"width": 3600, "height": 4320},
        "name": "Kids Hoodie",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Kids sizes, smaller print area",
    },
    "tank_top": {
        "blueprint_id": 10,
        "provider_id": 99,
        "print_area": {"width": 4500, "height": 5400},
        "name": "Women's Flowy Racerback Tank",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Sleeveless",
    },
    "long_sleeve": {
        "blueprint_id": 41,
        "provider_id": 99,
        "print_area": {"width": 4500, "height": 5400},
        "name": "Unisex Jersey Long Sleeve Tee",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Long sleeve variant",
    },
    "hoodie_unisex": {
        "blueprint_id": 92,
        "provider_id": 99,
        "print_area": {"width": 4500, "height": 5400},
        "name": "Unisex College Hoodie",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Classic pullover hoodie",
    },
    "hoodie_zip": {
        "blueprint_id": 91,
        "provider_id": 99,
        "print_area": {"width": 4500, "height": 5400},
        "name": "Unisex Full Zip Hoodie",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Zip-up hoodie",
    },
    "sweatshirt": {
        "blueprint_id": 49,
        "provider_id": 99,
        "print_area": {"width": 4500, "height": 5400},
        "name": "Unisex Heavy Blend™ Crewneck Sweatshirt",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "No hood",
    },
    # ========================================================================
    # HOME & LIVING - Full Coverage
    # ========================================================================
    "blanket_fleece": {
        "blueprint_id": 238,
        "provider_id": 99,
        "print_area": {"width": 6000, "height": 8000},
        "name": "Sherpa Fleece Blanket",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Full edge-to-edge print, plush fleece",
    },
    "blanket_medium": {
        "blueprint_id": 238,
        "provider_id": 99,
        "print_area": {"width": 4500, "height": 6000},
        "name": "Sherpa Fleece Blanket",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Medium size blanket",
    },
    "blanket_large": {
        "blueprint_id": 238,
        "provider_id": 99,
        "print_area": {"width": 7200, "height": 9000},
        "name": "Fleece Blanket 60x80",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Large size, full bed coverage",
    },
    "throw_pillow_14x14": {
        "blueprint_id": 220,
        "provider_id": 99,
        "print_area": {"width": 4200, "height": 4200},
        "name": "Spun Polyester Square Pillow",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Square pillow",
    },
    "throw_pillow_16x16": {
        "blueprint_id": 220,
        "provider_id": 99,
        "print_area": {"width": 4800, "height": 4800},
        "name": "Spun Polyester Square Pillow",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Large square pillow",
    },
    "throw_pillow_18x18": {
        "blueprint_id": 220,
        "provider_id": 99,
        "print_area": {"width": 5400, "height": 5400},
        "name": "Throw Pillow 18x18",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Extra large square pillow",
    },
    "lumbar_pillow": {
        "blueprint_id": 538,
        "provider_id": 99,
        "print_area": {"width": 6600, "height": 3600},
        "name": "Spun Polyester Lumbar Pillow",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Rectangular lumbar support",
    },
    "shower_curtain": {
        "blueprint_id": 235,
        "provider_id": 99,
        "print_area": {"width": 7200, "height": 7200},
        "name": "Shower Curtains",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Bathroom shower curtain",
    },
    "bath_towel": {
        "blueprint_id": 352,
        "provider_id": 99,
        "print_area": {"width": 8100, "height": 5400},
        "name": "Beach Towel",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Large bath towel",
    },
    "hand_towel": {
        "blueprint_id": 621,
        "provider_id": 99,
        "print_area": {"width": 4500, "height": 3000},
        "name": "Rally Towel",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Smaller hand towel",
    },
    "rug_small": {
        "blueprint_id": 438,
        "provider_id": 99,
        "print_area": {"width": 7200, "height": 4800},
        "name": "Area Rugs",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Small area rug",
    },
    "rug_medium": {
        "blueprint_id": 438,
        "provider_id": 99,
        "print_area": {"width": 9600, "height": 7200},
        "name": "Area Rugs",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Medium area rug",
    },
    "doormat": {
        "blueprint_id": 438,
        "provider_id": 99,
        "print_area": {"width": 5400, "height": 3600},
        "name": "Doormat 18x30",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Entry doormat",
    },
    "duvet_cover_twin": {
        "blueprint_id": 296,
        "provider_id": 99,
        "print_area": {"width": 8400, "height": 10200},
        "name": "Microfiber Duvet Cover",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Twin bed duvet",
    },
    "duvet_cover_queen": {
        "blueprint_id": 296,
        "provider_id": 99,
        "print_area": {"width": 10500, "height": 10500},
        "name": "Microfiber Duvet Cover",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Queen bed duvet",
    },
    "duvet_cover_king": {
        "blueprint_id": 296,
        "provider_id": 99,
        "print_area": {"width": 12300, "height": 10500},
        "name": "Duvet Cover King",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "King bed duvet",
    },
    # ========================================================================
    # WALL ART - Full Coverage
    # ========================================================================
    "poster_12x18": {
        "blueprint_id": 282,
        "provider_id": 99,
        "print_area": {"width": 3600, "height": 5400},
        "name": "Matte Vertical Posters",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Standard poster size",
    },
    "poster_18x24": {
        "blueprint_id": 282,
        "provider_id": 99,
        "print_area": {"width": 5400, "height": 7200},
        "name": "Matte Vertical Posters",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Large poster",
    },
    "poster_24x36": {
        "blueprint_id": 282,
        "provider_id": 99,
        "print_area": {"width": 7200, "height": 10800},
        "name": "Matte Vertical Posters",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Extra large poster",
    },
    "canvas_8x10": {
        "blueprint_id": 555,
        "provider_id": 99,
        "print_area": {"width": 2400, "height": 3000},
        "name": "Stretched Canvas",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Small canvas print",
    },
    "canvas_12x16": {
        "blueprint_id": 555,
        "provider_id": 99,
        "print_area": {"width": 3600, "height": 4800},
        "name": "Stretched Canvas",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Medium canvas",
    },
    "canvas_16x20": {
        "blueprint_id": 555,
        "provider_id": 99,
        "print_area": {"width": 4800, "height": 6000},
        "name": "Stretched Canvas",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Large canvas",
    },
    "canvas_18x24": {
        "blueprint_id": 555,
        "provider_id": 99,
        "print_area": {"width": 5400, "height": 7200},
        "name": "Stretched Canvas",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Extra large canvas",
    },
    "canvas_24x36": {
        "blueprint_id": 555,
        "provider_id": 99,
        "print_area": {"width": 7200, "height": 10800},
        "name": "Canvas 24x36",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Huge canvas",
    },
    "framed_print_12x16": {
        "blueprint_id": 492,
        "provider_id": 99,
        "print_area": {"width": 3600, "height": 4800},
        "name": "Vertical Framed Poster",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Framed wall art",
    },
    "framed_print_16x20": {
        "blueprint_id": 492,
        "provider_id": 99,
        "print_area": {"width": 4800, "height": 6000},
        "name": "Vertical Framed Poster",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "Large framed print",
    },
    # ========================================================================
    # DRINKWARE - Wrap/Transparent
    # ========================================================================
    "mug_11oz": {
        "blueprint_id": 68,
        "provider_id": 99,
        "print_area": {"width": 2475, "height": 1155},
        "name": "Mug 11oz",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Classic white mug, wrap-around print",
    },
    "mug_15oz": {
        "blueprint_id": 425,
        "provider_id": 99,
        "print_area": {"width": 2850, "height": 1155},
        "name": "Mug 15oz",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Large mug",
    },
    "travel_mug": {
        "blueprint_id": 353,
        "provider_id": 99,
        "print_area": {"width": 2550, "height": 1950},
        "name": "Tumbler 20oz",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Insulated travel mug",
    },
    "water_bottle": {
        "blueprint_id": 482,
        "provider_id": 99,
        "print_area": {"width": 2475, "height": 2400},
        "name": "Stainless Steel Water Bottle 17oz",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Insulated water bottle",
    },
    "wine_tumbler": {
        "blueprint_id": 354,
        "provider_id": 99,
        "print_area": {"width": 2475, "height": 1800},
        "name": "Tumbler 10oz",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Insulated wine tumbler",
    },
    # ========================================================================
    # ACCESSORIES - Mostly Transparent
    # ========================================================================
    "phone_case_iphone": {
        "blueprint_id": 77,
        "provider_id": 99,
        "print_area": {"width": 1875, "height": 3150},
        "name": "iPhone Tough Case",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "iPhone case, centered design",
    },
    "phone_case_samsung": {
        "blueprint_id": 269,
        "provider_id": 99,
        "print_area": {"width": 1875, "height": 3150},
        "name": "Tough Phone Cases",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Samsung case",
    },
    "tote_bag": {
        "blueprint_id": 467,
        "provider_id": 99,
        "print_area": {"width": 4500, "height": 5400},
        "name": "Tote Bag",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Reusable shopping bag",
    },
    "tote_bag_large": {
        "blueprint_id": 467,
        "provider_id": 99,
        "print_area": {"width": 6000, "height": 7200},
        "name": "Large Cotton Tote",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Extra large tote",
    },
    "sticker_3x3": {
        "blueprint_id": 380,
        "provider_id": 99,
        "print_area": {"width": 900, "height": 900},
        "name": "Kiss-Cut Stickers",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Die-cut sticker",
    },
    "sticker_4x4": {
        "blueprint_id": 380,
        "provider_id": 99,
        "print_area": {"width": 1200, "height": 1200},
        "name": "Square Sticker 4x4",
        "coverage_type": "transparent",
        "dpi": 300,
        "notes": "Larger sticker",
    },
    "notebook_spiral": {
        "blueprint_id": 74,
        "provider_id": 99,
        "print_area": {"width": 3000, "height": 4500},
        "name": "Spiral Notebook - Ruled Line",
        "coverage_type": "full",
        "dpi": 300,
        "notes": "5x7 notebook with custom cover",
    },
}


# ============================================================================
# Product Categories for Easy Filtering
# ============================================================================

PRODUCT_CATEGORIES = {
    "apparel": [
        "tshirt_unisex",
        "tshirt_premium",
        "tshirt_womens",
        "tshirt_kids",
        "tank_top",
        "long_sleeve",
        "hoodie_unisex",
        "hoodie_zip",
        "sweatshirt",
    ],
    "home_living": [
        "blanket_fleece",
        "blanket_medium",
        "blanket_large",
        "throw_pillow_14x14",
        "throw_pillow_16x16",
        "throw_pillow_18x18",
        "lumbar_pillow",
        "shower_curtain",
        "bath_towel",
        "hand_towel",
        "rug_small",
        "rug_medium",
        "doormat",
        "duvet_cover_twin",
        "duvet_cover_queen",
        "duvet_cover_king",
    ],
    "wall_art": [
        "poster_12x18",
        "poster_18x24",
        "poster_24x36",
        "canvas_8x10",
        "canvas_12x16",
        "canvas_16x20",
        "canvas_18x24",
        "canvas_24x36",
        "framed_print_12x16",
        "framed_print_16x20",
        "wood_print",
        "metal_print",
    ],
    "drinkware": [
        "mug_11oz",
        "mug_15oz",
        "travel_mug",
        "water_bottle",
        "wine_tumbler",
    ],
    "accessories": [
        "phone_case_iphone",
        "phone_case_samsung",
        "tote_bag",
        "tote_bag_large",
        "sticker_3x3",
        "sticker_4x4",
        "notebook_spiral",
        "mousepad",
        "yoga_mat",
        "beach_towel",
        "apron",
    ],
}


def get_products_by_category(category: str) -> list[str]:
    """Get all product IDs in a category.

    Args:
        category: Category name (apparel, home_living, wall_art, drinkware, accessories)

    Returns:
        List of product IDs
    """
    return PRODUCT_CATEGORIES.get(category, [])


def get_products_by_coverage(coverage_type: CoverageType) -> list[str]:
    """Get all products with specific coverage type.

    Args:
        coverage_type: "transparent", "full", or "centered"

    Returns:
        List of product IDs
    """
    return [
        product_id
        for product_id, spec in PRINTIFY_PRODUCTS.items()
        if spec["coverage_type"] == coverage_type
    ]


def get_all_product_ids() -> list[str]:
    """Get all available product IDs.

    Returns:
        List of all product IDs
    """
    return list(PRINTIFY_PRODUCTS.keys())
