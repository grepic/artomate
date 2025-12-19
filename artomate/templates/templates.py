"""Pre-made design templates for quick start."""

from typing import Dict, List, Any

# Template categories
TEMPLATES: Dict[str, Dict[str, Any]] = {
    # Minimalist templates
    "minimalist_cat": {
        "name": "Minimalist Cat",
        "theme": "cat",
        "style": "minimalist",
        "keywords": ["zen", "calm", "simple", "line art", "minimalist"],
        "niche": "home-decor",
        "description": "Simple, zen-inspired cat illustration perfect for minimalist interiors",
        "target_audience": "millennials, home decorators, minimalist enthusiasts",
        "price_range": {"min": 15.99, "max": 29.99},
        "recommended_products": ["tshirt", "poster_18x24", "canvas_16x20"],
        "seo_tags": ["minimalist art", "cat lover gift", "zen decor", "simple wall art"],
        "prompt_template": "minimalist line art of a {animal}, zen aesthetic, simple shapes, black and white, clean design",
    },
    "minimalist_mountains": {
        "name": "Minimalist Mountains",
        "theme": "mountains",
        "style": "minimalist",
        "keywords": ["nature", "peaceful", "serene", "landscape"],
        "niche": "home-decor",
        "description": "Clean mountain landscape with minimalist aesthetic",
        "target_audience": "nature lovers, hikers, modern home decorators",
        "price_range": {"min": 18.99, "max": 34.99},
        "recommended_products": ["poster_18x24", "canvas_16x20"],
        "seo_tags": ["mountain art", "minimalist landscape", "nature print"],
        "prompt_template": "minimalist mountain landscape, simple lines, clean aesthetic, {mood} atmosphere",
    },
    # Boho templates
    "boho_florals": {
        "name": "Boho Florals",
        "theme": "flowers",
        "style": "boho",
        "keywords": ["bohemian", "earthy", "natural", "colorful"],
        "niche": "lifestyle",
        "description": "Bohemian floral arrangement with earthy, natural tones",
        "target_audience": "boho enthusiasts, free spirits, festival goers",
        "price_range": {"min": 16.99, "max": 28.99},
        "recommended_products": ["tshirt", "poster_12x18", "mug"],
        "seo_tags": ["boho art", "floral design", "bohemian decor"],
        "prompt_template": "bohemian floral arrangement, earthy tones, watercolor style, {colors}",
    },
    "boho_mandala": {
        "name": "Boho Mandala",
        "theme": "mandala",
        "style": "boho",
        "keywords": ["spiritual", "meditation", "intricate", "peaceful"],
        "niche": "wellness",
        "description": "Intricate mandala design for meditation and mindfulness",
        "target_audience": "yoga practitioners, spiritual seekers, meditators",
        "price_range": {"min": 17.99, "max": 32.99},
        "recommended_products": ["poster_18x24", "canvas_16x20", "tshirt"],
        "seo_tags": ["mandala art", "meditation art", "spiritual decor"],
        "prompt_template": "intricate bohemian mandala, {colors}, detailed patterns, peaceful energy",
    },
    # Japandi templates
    "japandi_bamboo": {
        "name": "Japandi Bamboo",
        "theme": "bamboo",
        "style": "japandi",
        "keywords": ["zen", "minimal", "japanese", "scandinavian"],
        "niche": "home-decor",
        "description": "Zen bamboo illustration combining Japanese and Scandinavian aesthetics",
        "target_audience": "design enthusiasts, minimalists, zen seekers",
        "price_range": {"min": 19.99, "max": 36.99},
        "recommended_products": ["poster_18x24", "canvas_16x20"],
        "seo_tags": ["japandi art", "bamboo print", "zen decor", "minimalist japanese"],
        "prompt_template": "japandi style bamboo, minimalist zen aesthetic, neutral colors, {mood}",
    },
    # Geometric templates
    "geometric_abstract": {
        "name": "Geometric Abstract",
        "theme": "geometric pattern",
        "style": "modern",
        "keywords": ["abstract", "clean", "lines", "shapes"],
        "niche": "wall-art",
        "description": "Modern abstract geometric pattern",
        "target_audience": "modern home decorators, architects, design lovers",
        "price_range": {"min": 17.99, "max": 31.99},
        "recommended_products": ["poster_18x24", "canvas_16x20", "tshirt"],
        "seo_tags": ["geometric art", "abstract print", "modern wall art"],
        "prompt_template": "modern geometric abstract pattern, {colors}, clean lines, {mood}",
    },
    # Vintage templates
    "vintage_car": {
        "name": "Vintage Car",
        "theme": "vintage car",
        "style": "retro",
        "keywords": ["nostalgic", "classic", "automotive", "retro"],
        "niche": "apparel",
        "description": "Classic vintage car illustration with retro aesthetic",
        "target_audience": "car enthusiasts, vintage lovers, collectors",
        "price_range": {"min": 18.99, "max": 29.99},
        "recommended_products": ["tshirt", "hoodie", "poster_18x24"],
        "seo_tags": ["vintage car art", "retro automotive", "classic car print"],
        "prompt_template": "vintage {car_model} car, retro poster style, {era} aesthetic",
    },
    # Nature templates
    "nature_leaves": {
        "name": "Nature Leaves",
        "theme": "tropical leaves",
        "style": "modern",
        "keywords": ["botanical", "green", "natural", "fresh"],
        "niche": "home-decor",
        "description": "Fresh botanical leaf pattern",
        "target_audience": "plant lovers, tropical decor enthusiasts",
        "price_range": {"min": 15.99, "max": 27.99},
        "recommended_products": ["poster_12x18", "poster_18x24", "canvas_16x20"],
        "seo_tags": ["botanical art", "leaf print", "tropical decor"],
        "prompt_template": "modern botanical {leaf_type} leaves, fresh green tones, {style}",
    },
    # Motivational templates
    "motivational_quote": {
        "name": "Motivational Quote",
        "theme": "motivational quote",
        "style": "modern",
        "keywords": ["inspirational", "typography", "motivation", "positive"],
        "niche": "home-decor",
        "description": "Inspiring motivational quote with modern typography",
        "target_audience": "self-improvement seekers, office decorators",
        "price_range": {"min": 14.99, "max": 24.99},
        "recommended_products": ["poster_18x24", "tshirt"],
        "seo_tags": ["motivational art", "inspirational quote", "typography print"],
        "prompt_template": "modern typography design, {quote}, {colors}, clean minimal style",
    },
}


def get_template(template_id: str) -> Dict[str, Any]:
    """Get template by ID.

    Args:
        template_id: Template identifier

    Returns:
        Template dict

    Raises:
        KeyError: If template not found
    """
    if template_id not in TEMPLATES:
        raise KeyError(f"Template not found: {template_id}")

    return TEMPLATES[template_id]


def list_templates(category: str = None) -> List[Dict[str, Any]]:
    """List all available templates.

    Args:
        category: Optional category filter (e.g., "home-decor", "apparel")

    Returns:
        List of templates
    """
    templates = []

    for template_id, template in TEMPLATES.items():
        if category and template.get("niche") != category:
            continue

        templates.append(
            {
                "id": template_id,
                "name": template["name"],
                "theme": template["theme"],
                "style": template["style"],
                "niche": template.get("niche"),
                "description": template.get("description"),
            }
        )

    return templates


def get_template_categories() -> List[str]:
    """Get list of unique template categories.

    Returns:
        List of category names
    """
    categories = set()

    for template in TEMPLATES.values():
        if niche := template.get("niche"):
            categories.add(niche)

    return sorted(list(categories))


def apply_template(template_id: str, **overrides) -> Dict[str, Any]:
    """Apply template with optional overrides.

    Args:
        template_id: Template identifier
        **overrides: Fields to override in template

    Returns:
        Template dict with overrides applied

    Example:
        job_params = apply_template("minimalist_cat", animal="dog")
    """
    template = get_template(template_id).copy()

    # Apply overrides
    for key, value in overrides.items():
        if key in template:
            template[key] = value

    return template
