"""Product families with all size/color variants for comprehensive Printify coverage."""

from typing import Literal, TypedDict, List


CoverageType = Literal["transparent", "full", "centered"]


class ProductVariant(TypedDict):
    """Single variant specification (size, material, etc.)."""

    variant_id: str  # e.g., "12x18", "16x20"
    width: int  # Print area width in pixels
    height: int  # Print area height in pixels
    name: str  # Display name
    notes: str  # Additional notes


class ProductFamily(TypedDict):
    """Product family with all available variants."""

    family_id: str  # e.g., "poster", "canvas"
    name: str  # Display name
    blueprint_id: int  # Printify blueprint ID
    provider_id: int  # Printify provider ID
    coverage_type: CoverageType
    dpi: int
    category: str  # apparel, home_living, wall_art, drinkware, accessories
    variants: List[ProductVariant]
    notes: str


# ============================================================================
# COMPLETE PRODUCT FAMILIES WITH ALL VARIANTS
# ============================================================================

PRODUCT_FAMILIES: dict[str, ProductFamily] = {
    # ========================================================================
    # APPAREL - Transparent Background
    # ========================================================================
    "tshirt": {
        "family_id": "tshirt",
        "name": "Unisex T-Shirt",
        "blueprint_id": 3,
        "provider_id": 99,
        "coverage_type": "transparent",
        "dpi": 300,
        "category": "apparel",
        "variants": [
            # All sizes use same print area (Printify scales)
            {"variant_id": "standard", "width": 4500, "height": 5400, "name": "All Sizes", "notes": "S-5XL"}
        ],
        "notes": "Classic unisex tee, all sizes, multiple colors",
    },
    "tshirt_premium": {
        "family_id": "tshirt_premium",
        "name": "Premium T-Shirt",
        "blueprint_id": 5,
        "provider_id": 99,
        "coverage_type": "transparent",
        "dpi": 300,
        "category": "apparel",
        "variants": [
            {"variant_id": "standard", "width": 4500, "height": 5400, "name": "All Sizes", "notes": "S-3XL"}
        ],
        "notes": "Higher quality fabric",
    },
    "tshirt_womens": {
        "family_id": "tshirt_womens",
        "name": "Women's T-Shirt",
        "blueprint_id": 71,
        "provider_id": 99,
        "coverage_type": "transparent",
        "dpi": 300,
        "category": "apparel",
        "variants": [
            {"variant_id": "standard", "width": 4500, "height": 5400, "name": "All Sizes", "notes": "S-2XL"}
        ],
        "notes": "Fitted cut for women",
    },
    "hoodie": {
        "family_id": "hoodie",
        "name": "Unisex Hoodie",
        "blueprint_id": 77,
        "provider_id": 99,
        "coverage_type": "transparent",
        "dpi": 300,
        "category": "apparel",
        "variants": [
            {"variant_id": "standard", "width": 4500, "height": 5400, "name": "All Sizes", "notes": "S-5XL"}
        ],
        "notes": "Pullover hoodie, multiple colors",
    },
    "sweatshirt": {
        "family_id": "sweatshirt",
        "name": "Crewneck Sweatshirt",
        "blueprint_id": 146,
        "provider_id": 99,
        "coverage_type": "transparent",
        "dpi": 300,
        "category": "apparel",
        "variants": [
            {"variant_id": "standard", "width": 4500, "height": 5400, "name": "All Sizes", "notes": "S-5XL"}
        ],
        "notes": "No hood, cozy",
    },
    # ========================================================================
    # HOME & LIVING - Full Coverage
    # ========================================================================
    "blanket": {
        "family_id": "blanket",
        "name": "Fleece Blanket",
        "blueprint_id": 673,
        "provider_id": 99,
        "coverage_type": "full",
        "dpi": 300,
        "category": "home_living",
        "variants": [
            {"variant_id": "small", "width": 3600, "height": 4500, "name": "30x40", "notes": "Baby/lap blanket"},
            {"variant_id": "medium", "width": 4500, "height": 6000, "name": "40x50", "notes": "Throw blanket"},
            {"variant_id": "large", "width": 6000, "height": 8000, "name": "50x60", "notes": "Full blanket"},
            {"variant_id": "xlarge", "width": 7200, "height": 9000, "name": "60x80", "notes": "Queen/King size"},
        ],
        "notes": "Soft fleece, edge-to-edge print",
    },
    "pillow": {
        "family_id": "pillow",
        "name": "Throw Pillow",
        "blueprint_id": 27,
        "provider_id": 99,
        "coverage_type": "full",
        "dpi": 300,
        "category": "home_living",
        "variants": [
            {"variant_id": "14x14", "width": 4200, "height": 4200, "name": "14x14", "notes": "Small square"},
            {"variant_id": "16x16", "width": 4800, "height": 4800, "name": "16x16", "notes": "Medium square"},
            {"variant_id": "18x18", "width": 5400, "height": 5400, "name": "18x18", "notes": "Large square"},
            {"variant_id": "20x12", "width": 6000, "height": 3600, "name": "20x12", "notes": "Lumbar"},
            {"variant_id": "22x12", "width": 6600, "height": 3600, "name": "22x12", "notes": "Large lumbar"},
        ],
        "notes": "Square and rectangular options",
    },
    "towel": {
        "family_id": "towel",
        "name": "Towel",
        "blueprint_id": 822,
        "provider_id": 99,
        "coverage_type": "full",
        "dpi": 300,
        "category": "home_living",
        "variants": [
            {"variant_id": "hand", "width": 4500, "height": 3000, "name": "Hand Towel 15x30", "notes": "Small"},
            {"variant_id": "bath", "width": 8100, "height": 5400, "name": "Bath Towel 30x60", "notes": "Large"},
            {"variant_id": "beach", "width": 9000, "height": 6000, "name": "Beach Towel 30x60", "notes": "Extra thick"},
        ],
        "notes": "Absorbent, all-over print",
    },
    "rug": {
        "family_id": "rug",
        "name": "Area Rug",
        "blueprint_id": 1055,
        "provider_id": 99,
        "coverage_type": "full",
        "dpi": 300,
        "category": "home_living",
        "variants": [
            {"variant_id": "doormat", "width": 5400, "height": 3600, "name": "18x30 Doormat", "notes": "Entry"},
            {"variant_id": "small", "width": 7200, "height": 4800, "name": "24x36 Small", "notes": "Accent rug"},
            {"variant_id": "medium", "width": 9000, "height": 6000, "name": "36x60 Medium", "notes": "Room rug"},
            {"variant_id": "large", "width": 9600, "height": 7200, "name": "48x72 Large", "notes": "Large room"},
        ],
        "notes": "Non-slip backing",
    },
    "duvet": {
        "family_id": "duvet",
        "name": "Duvet Cover",
        "blueprint_id": 1015,
        "provider_id": 99,
        "coverage_type": "full",
        "dpi": 300,
        "category": "home_living",
        "variants": [
            {"variant_id": "twin", "width": 8400, "height": 10200, "name": "Twin 68x88", "notes": "Single bed"},
            {"variant_id": "queen", "width": 10500, "height": 10500, "name": "Queen 88x88", "notes": "Queen bed"},
            {"variant_id": "king", "width": 12300, "height": 10500, "name": "King 104x88", "notes": "King bed"},
        ],
        "notes": "Full edge-to-edge print on bedding",
    },
    # ========================================================================
    # WALL ART - Full Coverage
    # ========================================================================
    "poster": {
        "family_id": "poster",
        "name": "Poster",
        "blueprint_id": 6,
        "provider_id": 99,
        "coverage_type": "full",
        "dpi": 300,
        "category": "wall_art",
        "variants": [
            {"variant_id": "8x10", "width": 2400, "height": 3000, "name": "8x10", "notes": "Smallest"},
            {"variant_id": "12x16", "width": 3600, "height": 4800, "name": "12x16", "notes": "Small"},
            {"variant_id": "12x18", "width": 3600, "height": 5400, "name": "12x18", "notes": "Standard"},
            {"variant_id": "16x20", "width": 4800, "height": 6000, "name": "16x20", "notes": "Medium"},
            {"variant_id": "18x24", "width": 5400, "height": 7200, "name": "18x24", "notes": "Large"},
            {"variant_id": "24x36", "width": 7200, "height": 10800, "name": "24x36", "notes": "XL"},
        ],
        "notes": "Matte finish, 6 sizes available",
    },
    "canvas": {
        "family_id": "canvas",
        "name": "Canvas Print",
        "blueprint_id": 184,
        "provider_id": 99,
        "coverage_type": "full",
        "dpi": 300,
        "category": "wall_art",
        "variants": [
            {"variant_id": "8x8", "width": 2400, "height": 2400, "name": "8x8", "notes": "Square small"},
            {"variant_id": "10x10", "width": 3000, "height": 3000, "name": "10x10", "notes": "Square medium"},
            {"variant_id": "8x10", "width": 2400, "height": 3000, "name": "8x10", "notes": "Vertical small"},
            {"variant_id": "12x12", "width": 3600, "height": 3600, "name": "12x12", "notes": "Square large"},
            {"variant_id": "12x16", "width": 3600, "height": 4800, "name": "12x16", "notes": "Vertical medium"},
            {"variant_id": "16x16", "width": 4800, "height": 4800, "name": "16x16", "notes": "Square XL"},
            {"variant_id": "16x20", "width": 4800, "height": 6000, "name": "16x20", "notes": "Vertical large"},
            {"variant_id": "18x24", "width": 5400, "height": 7200, "name": "18x24", "notes": "Vertical XL"},
            {"variant_id": "24x36", "width": 7200, "height": 10800, "name": "24x36", "notes": "Vertical XXL"},
        ],
        "notes": "Gallery wrapped canvas, 9 sizes",
    },
    "framed_print": {
        "family_id": "framed_print",
        "name": "Framed Print",
        "blueprint_id": 19,
        "provider_id": 99,
        "coverage_type": "full",
        "dpi": 300,
        "category": "wall_art",
        "variants": [
            {"variant_id": "10x10", "width": 3000, "height": 3000, "name": "10x10", "notes": "Square"},
            {"variant_id": "12x16", "width": 3600, "height": 4800, "name": "12x16", "notes": "Medium"},
            {"variant_id": "16x20", "width": 4800, "height": 6000, "name": "16x20", "notes": "Large"},
            {"variant_id": "18x24", "width": 5400, "height": 7200, "name": "18x24", "notes": "XL"},
        ],
        "notes": "Black or white frame options",
    },
    # ========================================================================
    # DRINKWARE - Transparent Wrap
    # ========================================================================
    "mug": {
        "family_id": "mug",
        "name": "Ceramic Mug",
        "blueprint_id": 380,
        "provider_id": 99,
        "coverage_type": "transparent",
        "dpi": 300,
        "category": "drinkware",
        "variants": [
            {"variant_id": "11oz", "width": 2475, "height": 1155, "name": "11oz", "notes": "Standard size"},
            {"variant_id": "15oz", "width": 2850, "height": 1155, "name": "15oz", "notes": "Large size"},
        ],
        "notes": "White glossy, wrap-around print",
    },
    "travel_mug": {
        "family_id": "travel_mug",
        "name": "Travel Mug",
        "blueprint_id": 396,
        "provider_id": 99,
        "coverage_type": "transparent",
        "dpi": 300,
        "category": "drinkware",
        "variants": [
            {"variant_id": "15oz", "width": 2550, "height": 1950, "name": "15oz", "notes": "Insulated"},
        ],
        "notes": "Stainless steel, keeps hot/cold",
    },
    "water_bottle": {
        "family_id": "water_bottle",
        "name": "Water Bottle",
        "blueprint_id": 1016,
        "provider_id": 99,
        "coverage_type": "transparent",
        "dpi": 300,
        "category": "drinkware",
        "variants": [
            {"variant_id": "17oz", "width": 2475, "height": 2400, "name": "17oz", "notes": "Standard"},
            {"variant_id": "22oz", "width": 2475, "height": 2800, "name": "22oz", "notes": "Large"},
        ],
        "notes": "Insulated stainless steel",
    },
    # ========================================================================
    # ACCESSORIES - Mixed
    # ========================================================================
    "phone_case": {
        "family_id": "phone_case",
        "name": "Phone Case",
        "blueprint_id": 77,
        "provider_id": 99,
        "coverage_type": "transparent",
        "dpi": 300,
        "category": "accessories",
        "variants": [
            # Different phone models have different dimensions
            {"variant_id": "iphone_14", "width": 1875, "height": 3150, "name": "iPhone 14", "notes": "Standard"},
            {"variant_id": "iphone_14_pro", "width": 1875, "height": 3150, "name": "iPhone 14 Pro", "notes": "Pro"},
            {"variant_id": "samsung_s23", "width": 1875, "height": 3150, "name": "Samsung S23", "notes": "Android"},
        ],
        "notes": "Tough case, multiple phone models",
    },
    "tote_bag": {
        "family_id": "tote_bag",
        "name": "Tote Bag",
        "blueprint_id": 285,
        "provider_id": 99,
        "coverage_type": "transparent",
        "dpi": 300,
        "category": "accessories",
        "variants": [
            {"variant_id": "standard", "width": 4500, "height": 5400, "name": "Standard 15x16", "notes": "Regular"},
            {"variant_id": "large", "width": 6000, "height": 7200, "name": "Large 18x18", "notes": "Extra large"},
        ],
        "notes": "Cotton canvas, reusable",
    },
    "sticker": {
        "family_id": "sticker",
        "name": "Die-Cut Sticker",
        "blueprint_id": 342,
        "provider_id": 99,
        "coverage_type": "transparent",
        "dpi": 300,
        "category": "accessories",
        "variants": [
            {"variant_id": "2x2", "width": 600, "height": 600, "name": "2x2", "notes": "Mini"},
            {"variant_id": "3x3", "width": 900, "height": 900, "name": "3x3", "notes": "Small"},
            {"variant_id": "4x4", "width": 1200, "height": 1200, "name": "4x4", "notes": "Medium"},
            {"variant_id": "5.5x5.5", "width": 1650, "height": 1650, "name": "5.5x5.5", "notes": "Large"},
        ],
        "notes": "Weatherproof, kiss-cut",
    },
}


# ============================================================================
# Helper Functions
# ============================================================================


def get_all_family_ids() -> List[str]:
    """Get all product family IDs.

    Returns:
        List of family IDs
    """
    return list(PRODUCT_FAMILIES.keys())


def get_family_by_category(category: str) -> List[str]:
    """Get all product families in a category.

    Args:
        category: Category name

    Returns:
        List of family IDs
    """
    return [
        family_id
        for family_id, family in PRODUCT_FAMILIES.items()
        if family["category"] == category
    ]


def get_total_variants(family_id: str) -> int:
    """Get total number of variants for a family.

    Args:
        family_id: Product family ID

    Returns:
        Number of variants
    """
    if family_id not in PRODUCT_FAMILIES:
        return 0

    return len(PRODUCT_FAMILIES[family_id]["variants"])


def get_all_variants_summary() -> dict:
    """Get summary of all variants across all families.

    Returns:
        Dict with summary statistics
    """
    total_families = len(PRODUCT_FAMILIES)
    total_variants = sum(len(f["variants"]) for f in PRODUCT_FAMILIES.values())

    by_category = {}
    for family in PRODUCT_FAMILIES.values():
        cat = family["category"]
        if cat not in by_category:
            by_category[cat] = {"families": 0, "variants": 0}
        by_category[cat]["families"] += 1
        by_category[cat]["variants"] += len(family["variants"])

    return {
        "total_families": total_families,
        "total_variants": total_variants,
        "by_category": by_category,
    }
