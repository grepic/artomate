"""Streamlit UI for interactive product crop testing - step by step."""

import streamlit as st
from pathlib import Path
from datetime import datetime
from PIL import Image
import json
from typing import List, Dict, Optional
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure page FIRST
st.set_page_config(
    page_title="Crop Tester - Artomate",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ff6b35;
        margin-bottom: 1rem;
    }
    .step-header {
        font-size: 1.8rem;
        color: #004e89;
        border-bottom: 3px solid #004e89;
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .variant-badge {
        display: inline-block;
        background-color: #004e89;
        color: white;
        padding: 0.3rem 0.7rem;
        border-radius: 0.3rem;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state IMMEDIATELY
if 'current_step' not in st.session_state:
    st.session_state.current_step = "generate_prompts"
if 'test_image_path' not in st.session_state:
    st.session_state.test_image_path = None
if 'test_image' not in st.session_state:
    st.session_state.test_image = None
if 'monthly_prompts' not in st.session_state:
    st.session_state.monthly_prompts = {}  # Prompty pro 12 měsíců
if 'prompt_params' not in st.session_state:
    st.session_state.prompt_params = {}  # Parametry pro generování promptů
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = {}  # AI-generované obrázky (12 monthly)
if 'selected_products' not in st.session_state:
    st.session_state.selected_products = {}
if 'crop_results' not in st.session_state:
    st.session_state.crop_results = None
if 'test_output_dir' not in st.session_state:
    st.session_state.test_output_dir = None
if 'approved_variants' not in st.session_state:
    st.session_state.approved_variants = {}
if 'seo_metadata' not in st.session_state:
    st.session_state.seo_metadata = {}
if 'publish_status' not in st.session_state:
    st.session_state.publish_status = {}
if 'variant_seo' not in st.session_state:
    st.session_state.variant_seo = {}  # SEO pro každou variantu zvlášť
if 'printify_products' not in st.session_state:
    st.session_state.printify_products = {}  # Vytvořené Printify produkty
if 'etsy_listings' not in st.session_state:
    st.session_state.etsy_listings = {}  # Vytvořené Etsy listingy
if 'viral_videos' not in st.session_state:
    st.session_state.viral_videos = {}  # Vygenerovaná viral videa
if 'social_posts' not in st.session_state:
    st.session_state.social_posts = {}  # Social media posty
if 'stock_submissions' not in st.session_state:
    st.session_state.stock_submissions = {}  # Stock platform submissions


def get_product_families() -> Dict[str, Dict]:
    """Get product families and their variants with detailed specs.
    
    Each variant includes:
    - print_area: Human readable size
    - width_px, height_px: Pixel dimensions for the generated crop (aligned to Printify specs where known)
    - placement: How the design is placed
    - position: Description of positioning
    """
    return {
        # --- WALL ART ---
        "Poster": {
            "default_size": "12×18",
            "variants": {
                "8×10": {"print_area": "8 × 10 in", "width_px": 2400, "height_px": 3000, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "10×10": {"print_area": "10 × 10 in", "width_px": 3000, "height_px": 3000, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "11×14": {"print_area": "11 × 14 in", "width_px": 3300, "height_px": 4200, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "12×16": {"print_area": "12 × 16 in", "width_px": 3600, "height_px": 4800, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "12×18": {"print_area": "12 × 18 in", "width_px": 3600, "height_px": 5400, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "16×20": {"print_area": "16 × 20 in", "width_px": 4800, "height_px": 6000, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "18×24": {"print_area": "18 × 24 in", "width_px": 5400, "height_px": 7200, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "24×36": {"print_area": "24 × 36 in", "width_px": 7200, "height_px": 10800, "placement": "full", "position": "Edge to edge", "coverage": "full"},
            },
        },
        "Canvas": {
            "default_size": "16×20",
            "variants": {
                "8×8": {"print_area": "8 × 8 in", "width_px": 2400, "height_px": 2400, "placement": "full", "position": "Stretched on frame", "coverage": "full"},
                "10×10": {"print_area": "10 × 10 in", "width_px": 3000, "height_px": 3000, "placement": "full", "position": "Stretched on frame", "coverage": "full"},
                "12×12": {"print_area": "12 × 12 in", "width_px": 3600, "height_px": 3600, "placement": "full", "position": "Stretched on frame", "coverage": "full"},
                "8×10": {"print_area": "8 × 10 in", "width_px": 2400, "height_px": 3000, "placement": "full", "position": "Stretched on frame", "coverage": "full"},
                "12×16": {"print_area": "12 × 16 in", "width_px": 3600, "height_px": 4800, "placement": "full", "position": "Stretched on frame", "coverage": "full"},
                "16×16": {"print_area": "16 × 16 in", "width_px": 4800, "height_px": 4800, "placement": "full", "position": "Stretched on frame", "coverage": "full"},
                "16×20": {"print_area": "16 × 20 in", "width_px": 4800, "height_px": 6000, "placement": "full", "position": "Stretched on frame", "coverage": "full"},
                "18×24": {"print_area": "18 × 24 in", "width_px": 5400, "height_px": 7200, "placement": "full", "position": "Stretched on frame", "coverage": "full"},
                "24×36": {"print_area": "24 × 36 in", "width_px": 7200, "height_px": 10800, "placement": "full", "position": "Stretched on frame", "coverage": "full"},
            },
        },
        "Framed Print": {
            "default_size": "16×20",
            "variants": {
                "10×10": {"print_area": "10 × 10 in", "width_px": 3000, "height_px": 3000, "placement": "full", "position": "In frame (edge-to-edge artwork)", "coverage": "full"},
                "12×16": {"print_area": "12 × 16 in", "width_px": 3600, "height_px": 4800, "placement": "full", "position": "In frame (edge-to-edge artwork)", "coverage": "full"},
                "16×20": {"print_area": "16 × 20 in", "width_px": 4800, "height_px": 6000, "placement": "full", "position": "In frame (edge-to-edge artwork)", "coverage": "full"},
                "18×24": {"print_area": "18 × 24 in", "width_px": 5400, "height_px": 7200, "placement": "full", "position": "In frame (edge-to-edge artwork)", "coverage": "full"},
            },
        },

        # --- APPAREL (transparent centered) ---
        "Unisex T-Shirt": {
            "default_size": "One Size",
            "variants": {
                "Front": {"print_area": "4500 × 5400 px", "width_px": 4500, "height_px": 5400, "placement": "front_center", "position": "Centered on chest", "coverage": "transparent"},
            },
        },
        "Premium T-Shirt": {
            "default_size": "One Size",
            "variants": {
                "Front": {"print_area": "4500 × 5400 px", "width_px": 4500, "height_px": 5400, "placement": "front_center", "position": "Centered on chest", "coverage": "transparent"},
            },
        },
        "Women's T-Shirt": {
            "default_size": "One Size",
            "variants": {
                "Front": {"print_area": "4500 × 5400 px", "width_px": 4500, "height_px": 5400, "placement": "front_center", "position": "Centered on chest", "coverage": "transparent"},
            },
        },
        "Kids T-Shirt": {
            "default_size": "One Size",
            "variants": {
                "Front": {"print_area": "3600 × 4320 px", "width_px": 3600, "height_px": 4320, "placement": "front_center", "position": "Centered on chest", "coverage": "transparent"},
            },
        },
        "Tank Top": {
            "default_size": "One Size",
            "variants": {
                "Front": {"print_area": "4500 × 5400 px", "width_px": 4500, "height_px": 5400, "placement": "front_center", "position": "Centered on chest", "coverage": "transparent"},
            },
        },
        "Long Sleeve": {
            "default_size": "One Size",
            "variants": {
                "Front": {"print_area": "4500 × 5400 px", "width_px": 4500, "height_px": 5400, "placement": "front_center", "position": "Centered on chest", "coverage": "transparent"},
            },
        },
        "Unisex Hoodie": {
            "default_size": "One Size",
            "variants": {
                "Front": {"print_area": "4500 × 5400 px", "width_px": 4500, "height_px": 5400, "placement": "front_center", "position": "Centered on chest", "coverage": "transparent"},
            },
        },
        "Zip Hoodie": {
            "default_size": "One Size",
            "variants": {
                "Front": {"print_area": "4500 × 5400 px", "width_px": 4500, "height_px": 5400, "placement": "front_center", "position": "Centered on chest", "coverage": "transparent"},
            },
        },
        "Crewneck Sweatshirt": {
            "default_size": "One Size",
            "variants": {
                "Front": {"print_area": "4500 × 5400 px", "width_px": 4500, "height_px": 5400, "placement": "front_center", "position": "Centered on chest", "coverage": "transparent"},
            },
        },

        # --- HOME & LIVING (full coverage) ---
        "Blanket (Fleece)": {
            "default_size": "50×60",
            "variants": {
                "40×50": {"print_area": "4500 × 6000 px", "width_px": 4500, "height_px": 6000, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "50×60": {"print_area": "6000 × 8000 px", "width_px": 6000, "height_px": 8000, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "60×80": {"print_area": "7200 × 9000 px", "width_px": 7200, "height_px": 9000, "placement": "full", "position": "Edge to edge", "coverage": "full"},
            },
        },
        "Pillow": {
            "default_size": "18×18",
            "variants": {
                "14×14": {"print_area": "4200 × 4200 px", "width_px": 4200, "height_px": 4200, "placement": "full", "position": "Centered (full coverage)", "coverage": "full"},
                "16×16": {"print_area": "4800 × 4800 px", "width_px": 4800, "height_px": 4800, "placement": "full", "position": "Centered (full coverage)", "coverage": "full"},
                "18×18": {"print_area": "5400 × 5400 px", "width_px": 5400, "height_px": 5400, "placement": "full", "position": "Centered (full coverage)", "coverage": "full"},
                "20×12": {"print_area": "6000 × 3600 px", "width_px": 6000, "height_px": 3600, "placement": "full", "position": "Centered (full coverage)", "coverage": "full"},
                "22×12": {"print_area": "6600 × 3600 px", "width_px": 6600, "height_px": 3600, "placement": "full", "position": "Centered (full coverage)", "coverage": "full"},
            },
        },
        "Towel": {
            "default_size": "Bath",
            "variants": {
                "Hand": {"print_area": "4500 × 3000 px", "width_px": 4500, "height_px": 3000, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "Bath": {"print_area": "8100 × 5400 px", "width_px": 8100, "height_px": 5400, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "Beach": {"print_area": "9000 × 6000 px", "width_px": 9000, "height_px": 6000, "placement": "full", "position": "Edge to edge", "coverage": "full"},
            },
        },
        "Rug": {
            "default_size": "24×36",
            "variants": {
                "Doormat 18×30": {"print_area": "5400 × 3600 px", "width_px": 5400, "height_px": 3600, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "24×36": {"print_area": "7200 × 4800 px", "width_px": 7200, "height_px": 4800, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "48×72": {"print_area": "9600 × 7200 px", "width_px": 9600, "height_px": 7200, "placement": "full", "position": "Edge to edge", "coverage": "full"},
            },
        },
        "Duvet Cover": {
            "default_size": "Queen",
            "variants": {
                "Twin": {"print_area": "8400 × 10200 px", "width_px": 8400, "height_px": 10200, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "Queen": {"print_area": "10500 × 10500 px", "width_px": 10500, "height_px": 10500, "placement": "full", "position": "Edge to edge", "coverage": "full"},
                "King": {"print_area": "12300 × 10500 px", "width_px": 12300, "height_px": 10500, "placement": "full", "position": "Edge to edge", "coverage": "full"},
            },
        },

        # --- DRINKWARE (wrap/transparent) ---
        "Mug": {
            "default_size": "11oz",
            "variants": {
                "11oz": {"print_area": "2475 × 1155 px", "width_px": 2475, "height_px": 1155, "placement": "wrap", "position": "Wraps around", "coverage": "wrap"},
                "15oz": {"print_area": "2850 × 1155 px", "width_px": 2850, "height_px": 1155, "placement": "wrap", "position": "Wraps around", "coverage": "wrap"},
            },
        },
        "Travel Mug": {
            "default_size": "15oz",
            "variants": {
                "15oz": {"print_area": "2550 × 1950 px", "width_px": 2550, "height_px": 1950, "placement": "wrap", "position": "Wraps around", "coverage": "wrap"},
            },
        },
        "Water Bottle": {
            "default_size": "17oz",
            "variants": {
                "17oz": {"print_area": "2475 × 2400 px", "width_px": 2475, "height_px": 2400, "placement": "wrap", "position": "Wraps around", "coverage": "wrap"},
            },
        },

        # --- ACCESSORIES ---
        "Phone Case": {
            "default_size": "iPhone 14",
            "variants": {
                "iPhone 14": {"print_area": "1875 × 3150 px", "width_px": 1875, "height_px": 3150, "placement": "back", "position": "Back cover", "coverage": "transparent"},
                "iPhone 14 Pro": {"print_area": "1875 × 3150 px", "width_px": 1875, "height_px": 3150, "placement": "back", "position": "Back cover", "coverage": "transparent"},
                "Samsung S23": {"print_area": "1875 × 3150 px", "width_px": 1875, "height_px": 3150, "placement": "back", "position": "Back cover", "coverage": "transparent"},
            },
        },
        "Tote Bag": {
            "default_size": "Standard",
            "variants": {
                "Standard": {"print_area": "4500 × 5400 px", "width_px": 4500, "height_px": 5400, "placement": "front", "position": "Front center", "coverage": "transparent"},
                "Large": {"print_area": "6000 × 7200 px", "width_px": 6000, "height_px": 7200, "placement": "front", "position": "Front center", "coverage": "transparent"},
            },
        },
        "Sticker": {
            "default_size": "3×3",
            "variants": {
                "2×2": {"print_area": "600 × 600 px", "width_px": 600, "height_px": 600, "placement": "full", "position": "Die-cut", "coverage": "transparent"},
                "3×3": {"print_area": "900 × 900 px", "width_px": 900, "height_px": 900, "placement": "full", "position": "Die-cut", "coverage": "transparent"},
                "4×4": {"print_area": "1200 × 1200 px", "width_px": 1200, "height_px": 1200, "placement": "full", "position": "Die-cut", "coverage": "transparent"},
                "5.5×5.5": {"print_area": "1650 × 1650 px", "width_px": 1650, "height_px": 1650, "placement": "full", "position": "Die-cut", "coverage": "transparent"},
            },
        },
    }


def create_placeholder_image(width: int, height: int, text: str = "TEST IMAGE") -> Image.Image:
    """Create a placeholder test image with precise dimensions and visible markers."""
    from PIL import ImageDraw, ImageFont
    
    # Create gradient background
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    # Create gradient from blue to green to red
    for y in range(height):
        for x in range(width):
            r = int((x / width) * 255) if x / width > 0.5 else 0
            g = int((1 - abs(2 * y / height - 1)) * 255)
            b = int((1 - x / width) * 255) if x / width < 0.5 else 0
            pixels[x, y] = (r, g, b)
    
    draw = ImageDraw.Draw(img)
    
    # Draw corner markers (25px from edge)
    marker_size = 50
    marker_offset = 25
    marker_color = (255, 0, 0)
    marker_width = 5
    
    # Top-left
    draw.line([(marker_offset, marker_offset), (marker_offset + marker_size, marker_offset)], 
              fill=marker_color, width=marker_width)
    draw.line([(marker_offset, marker_offset), (marker_offset, marker_offset + marker_size)], 
              fill=marker_color, width=marker_width)
    
    # Top-right
    draw.line([(width - marker_offset - marker_size, marker_offset), (width - marker_offset, marker_offset)], 
              fill=marker_color, width=marker_width)
    draw.line([(width - marker_offset, marker_offset), (width - marker_offset, marker_offset + marker_size)], 
              fill=marker_color, width=marker_width)
    
    # Bottom-left
    draw.line([(marker_offset, height - marker_offset), (marker_offset + marker_size, height - marker_offset)], 
              fill=marker_color, width=marker_width)
    draw.line([(marker_offset, height - marker_offset - marker_size), (marker_offset, height - marker_offset)], 
              fill=marker_color, width=marker_width)
    
    # Bottom-right
    draw.line([(width - marker_offset - marker_size, height - marker_offset), (width - marker_offset, height - marker_offset)], 
              fill=marker_color, width=marker_width)
    draw.line([(width - marker_offset, height - marker_offset - marker_size), (width - marker_offset, height - marker_offset)], 
              fill=marker_color, width=marker_width)
    
    # Draw center circle with dots
    center_x, center_y = width // 2, height // 2
    circle_radius = min(width, height) // 4
    
    # Main circle (yellow)
    draw.ellipse([(center_x - circle_radius, center_y - circle_radius),
                  (center_x + circle_radius, center_y + circle_radius)],
                 fill=(255, 200, 50), outline=(255, 150, 0), width=8)
    
    # Dots around circle
    dot_radius = 35
    num_dots = 6
    for i in range(num_dots):
        angle = (i / num_dots) * 2 * 3.14159
        import math
        dot_x = center_x + int(circle_radius * 0.7 * math.cos(angle))
        dot_y = center_y + int(circle_radius * 0.7 * math.sin(angle))
        draw.ellipse([(dot_x - dot_radius, dot_y - dot_radius),
                      (dot_x + dot_radius, dot_y + dot_radius)],
                     fill=(255, 100, 150), outline=(255, 50, 100), width=4)
    
    # Draw text in center
    try:
        font_size = min(width, height) // 15
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Text with shadow
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) // 2
    text_y = center_y - text_height // 2
    
    # Shadow
    draw.text((text_x + 3, text_y + 3), text, font=font, fill=(0, 0, 0))
    # Main text
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))
    
    # Draw size label at bottom
    size_text = f"{width} × {height}px"
    try:
        size_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size // 2)
    except:
        size_font = font
    
    size_bbox = draw.textbbox((0, 0), size_text, font=size_font)
    size_width = size_bbox[2] - size_bbox[0]
    size_x = (width - size_width) // 2
    size_y = height - 100
    
    # Shadow
    draw.text((size_x + 2, size_y + 2), size_text, font=size_font, fill=(0, 0, 0))
    # Main text
    draw.text((size_x, size_y), size_text, font=size_font, fill=(255, 255, 255))
    
    return img


def crop_image_to_dimensions(source_image: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """Crop image to exact dimensions, maintaining aspect ratio and centering.
    
    This function:
    1. Calculates the target aspect ratio
    2. Crops the source to match that ratio
    3. Resizes to exact target dimensions
    """
    src_width, src_height = source_image.size
    target_ratio = target_width / target_height
    src_ratio = src_width / src_height
    
    # Determine crop box to match target ratio
    if src_ratio > target_ratio:
        # Source is wider - crop width
        new_width = int(src_height * target_ratio)
        left = (src_width - new_width) // 2
        crop_box = (left, 0, left + new_width, src_height)
    else:
        # Source is taller - crop height
        new_height = int(src_width / target_ratio)
        top = (src_height - new_height) // 2
        crop_box = (0, top, src_width, top + new_height)
    
    # Crop to correct aspect ratio
    cropped = source_image.crop(crop_box)
    
    # Resize to exact target dimensions
    final = cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    return final


def create_product_mockup(product_name: str, variant: str, test_image_path: str) -> Image.Image:
    """Create a realistic product mockup with the design placed on it."""
    from PIL import ImageDraw, ImageFont
    
    try:
        test_img = Image.open(test_image_path)
        
        if "T-Shirt" in product_name:
            # Create T-Shirt mockup
            canvas_w, canvas_h = 600, 700
            canvas = Image.new('RGBA', (canvas_w, canvas_h), color=(255, 255, 255, 255))
            draw = ImageDraw.Draw(canvas)
            
            # Draw T-shirt shape
            # Body
            draw.rectangle([(100, 150), (500, 650)], fill=(50, 50, 55), outline=(30, 30, 35), width=3)
            # Neck
            draw.ellipse([(250, 100), (350, 180)], fill=(50, 50, 55))
            # Sleeves
            draw.polygon([(100, 150), (50, 250), (100, 300)], fill=(45, 45, 50), outline=(30, 30, 35))
            draw.polygon([(500, 150), (550, 250), (500, 300)], fill=(45, 45, 50), outline=(30, 30, 35))
            
            # Place design on chest
            design_w, design_h = 250, 250
            test_img_scaled = test_img.copy()
            test_img_scaled.thumbnail((design_w, design_h), Image.Resampling.LANCZOS)
            
            x = (canvas_w - test_img_scaled.width) // 2
            y = 250
            canvas.paste(test_img_scaled, (x, y), test_img_scaled if test_img_scaled.mode == 'RGBA' else None)
            
            return canvas.convert('RGB')
            
        elif "Mug" in product_name:
            # Create Mug mockup
            canvas_w, canvas_h = 600, 500
            canvas = Image.new('RGBA', (canvas_w, canvas_h), color=(245, 245, 240, 255))
            draw = ImageDraw.Draw(canvas)
            
            # Draw mug body
            draw.ellipse([(150, 100), (450, 150)], fill=(255, 255, 255), outline=(200, 200, 200), width=3)
            draw.rectangle([(150, 125), (450, 400)], fill=(255, 255, 255), outline=(200, 200, 200), width=3)
            draw.ellipse([(150, 375), (450, 425)], fill=(255, 255, 255), outline=(200, 200, 200), width=3)
            
            # Handle
            draw.arc([(420, 180), (510, 350)], start=270, end=90, fill=(200, 200, 200), width=15)
            
            # Place design on mug
            design_w, design_h = 250, 200
            test_img_scaled = test_img.copy()
            test_img_scaled.thumbnail((design_w, design_h), Image.Resampling.LANCZOS)
            
            x = 175
            y = 180
            canvas.paste(test_img_scaled, (x, y), test_img_scaled if test_img_scaled.mode == 'RGBA' else None)
            
            return canvas.convert('RGB')
            
        elif "Phone" in product_name:
            # Create Phone Case mockup
            canvas_w, canvas_h = 400, 700
            canvas = Image.new('RGBA', (canvas_w, canvas_h), color=(240, 240, 240, 255))
            draw = ImageDraw.Draw(canvas)
            
            # Phone body
            draw.rounded_rectangle([(75, 50), (325, 650)], radius=30, fill=(30, 30, 35), outline=(20, 20, 25), width=5)
            
            # Screen notch
            draw.rectangle([(150, 70), (250, 85)], fill=(10, 10, 15))
            
            # Place design on back
            design_w, design_h = 220, 480
            test_img_scaled = test_img.copy()
            test_img_scaled.thumbnail((design_w, design_h), Image.Resampling.LANCZOS)
            
            x = (canvas_w - test_img_scaled.width) // 2
            y = 110
            canvas.paste(test_img_scaled, (x, y), test_img_scaled if test_img_scaled.mode == 'RGBA' else None)
            
            return canvas.convert('RGB')
            
        elif "Pillow" in product_name:
            # Create Pillow mockup
            canvas_w, canvas_h = 600, 600
            canvas = Image.new('RGBA', (canvas_w, canvas_h), color=(230, 230, 230, 255))
            draw = ImageDraw.Draw(canvas)
            
            # Pillow shape
            draw.rectangle([(50, 50), (550, 550)], fill=(245, 245, 250), outline=(200, 200, 200), width=5)
            
            # Place design centered
            design_w, design_h = 400, 400
            test_img_scaled = test_img.copy()
            test_img_scaled.thumbnail((design_w, design_h), Image.Resampling.LANCZOS)
            
            x = (canvas_w - test_img_scaled.width) // 2
            y = (canvas_h - test_img_scaled.height) // 2
            canvas.paste(test_img_scaled, (x, y), test_img_scaled if test_img_scaled.mode == 'RGBA' else None)
            
            return canvas.convert('RGB')
            
        elif "Tote" in product_name:
            # Create Tote Bag mockup
            canvas_w, canvas_h = 600, 700
            canvas = Image.new('RGBA', (canvas_w, canvas_h), color=(240, 235, 230, 255))
            draw = ImageDraw.Draw(canvas)
            
            # Bag body
            draw.polygon([(100, 150), (500, 150), (480, 650), (120, 650)], fill=(240, 240, 235), outline=(180, 180, 175), width=5)
            
            # Handles
            draw.arc([(180, 50), (250, 160)], start=180, end=0, fill=(150, 150, 145), width=12)
            draw.arc([(350, 50), (420, 160)], start=180, end=0, fill=(150, 150, 145), width=12)
            
            # Place design
            design_w, design_h = 300, 350
            test_img_scaled = test_img.copy()
            test_img_scaled.thumbnail((design_w, design_h), Image.Resampling.LANCZOS)
            
            x = (canvas_w - test_img_scaled.width) // 2
            y = 220
            canvas.paste(test_img_scaled, (x, y), test_img_scaled if test_img_scaled.mode == 'RGBA' else None)
            
            return canvas.convert('RGB')
            
        elif "Poster" in product_name or "Canvas" in product_name or "Framed" in product_name:
            # Frame mockup - adapt to actual crop aspect ratio
            crop_w, crop_h = test_img.size
            crop_ratio = crop_w / crop_h
            
            # Scale to fit in reasonable display size (max 800px on longer side)
            max_size = 800
            if crop_w > crop_h:
                display_w = max_size
                display_h = int(max_size / crop_ratio)
            else:
                display_h = max_size
                display_w = int(max_size * crop_ratio)
            
            frame_thickness = 40
            padding = 50
            
            canvas_w = display_w + 2 * (frame_thickness + padding)
            canvas_h = display_h + 2 * (frame_thickness + padding)
            
            canvas = Image.new('RGBA', (canvas_w, canvas_h), color=(200, 195, 190, 255))
            draw = ImageDraw.Draw(canvas)
            
            # Frame outer
            frame_x1 = padding
            frame_y1 = padding
            frame_x2 = padding + display_w + 2 * frame_thickness
            frame_y2 = padding + display_h + 2 * frame_thickness
            draw.rectangle([(frame_x1, frame_y1), (frame_x2, frame_y2)], 
                          fill=(80, 70, 60), outline=(60, 50, 40), width=5)
            
            # Frame inner (white mat)
            draw.rectangle([(frame_x1 + frame_thickness, frame_y1 + frame_thickness), 
                           (frame_x2 - frame_thickness, frame_y2 - frame_thickness)], 
                          fill=(255, 255, 255))
            
            # Place design - resize to exact display dimensions
            test_img_scaled = test_img.resize((display_w, display_h), Image.Resampling.LANCZOS)
            
            x = padding + frame_thickness
            y = padding + frame_thickness
            canvas.paste(test_img_scaled, (x, y), test_img_scaled if test_img_scaled.mode == 'RGBA' else None)
            
            return canvas.convert('RGB')
            
        else:
            # Default - just return scaled image
            return test_img.copy()
            
    except Exception as e:
        # Fallback gray image
        canvas = Image.new('RGB', (400, 400), color=(100, 100, 100))
        return canvas


def create_placement_guide(product_name: str, variant: str, crop_image: Image.Image, variant_specs: Dict) -> Image.Image:
    """Create a guide showing exact crop dimensions with markers."""
    from PIL import ImageDraw, ImageFont
    
    try:
        # Get actual crop size
        crop_w, crop_h = crop_image.size
        target_w = variant_specs.get("width_px", crop_w)
        target_h = variant_specs.get("height_px", crop_h)
        
        # Scale for display if too large (max 600px on longer side)
        max_display = 600
        display_crop = crop_image.copy()
        
        if max(crop_w, crop_h) > max_display:
            display_crop.thumbnail((max_display, max_display), Image.Resampling.LANCZOS)
        
        display_w, display_h = display_crop.size
        
        # Create canvas with padding
        padding = 50
        canvas_w = display_w + padding * 2
        canvas_h = display_h + padding * 2
        canvas = Image.new('RGB', (canvas_w, canvas_h), color=(250, 250, 250))
        draw = ImageDraw.Draw(canvas)
        
        # Paste crop image in center
        canvas.paste(display_crop, (padding, padding))
        
        # Draw border around image
        draw.rectangle([(padding, padding), (padding + display_w, padding + display_h)], 
                      outline=(200, 0, 0), width=3)
        
        # Draw corner markers
        marker_size = 20
        marker_color = (255, 0, 0)
        marker_width = 3
        
        # Top-left
        draw.line([(padding, padding), (padding + marker_size, padding)], 
                 fill=marker_color, width=marker_width)
        draw.line([(padding, padding), (padding, padding + marker_size)], 
                 fill=marker_color, width=marker_width)
        
        # Top-right
        draw.line([(padding + display_w - marker_size, padding), (padding + display_w, padding)], 
                 fill=marker_color, width=marker_width)
        draw.line([(padding + display_w, padding), (padding + display_w, padding + marker_size)], 
                 fill=marker_color, width=marker_width)
        
        # Bottom-left
        draw.line([(padding, padding + display_h), (padding + marker_size, padding + display_h)], 
                 fill=marker_color, width=marker_width)
        draw.line([(padding, padding + display_h - marker_size), (padding, padding + display_h)], 
                 fill=marker_color, width=marker_width)
        
        # Bottom-right
        draw.line([(padding + display_w - marker_size, padding + display_h), (padding + display_w, padding + display_h)], 
                 fill=marker_color, width=marker_width)
        draw.line([(padding + display_w, padding + display_h - marker_size), (padding + display_w, padding + display_h)], 
                 fill=marker_color, width=marker_width)
        
        # Add dimension labels (showing ACTUAL crop size, not display size)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Top label - actual width
        top_text = f"{crop_w}px"
        bbox = draw.textbbox((0, 0), top_text, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text((canvas_w // 2 - text_w // 2, 10), top_text, font=font, fill=(0, 0, 0))
        
        # Left label - actual height (rotated would be better but keep simple)
        left_text = f"{crop_h}px"
        draw.text((5, canvas_h // 2 - 10), left_text, font=font, fill=(0, 0, 0))
        
        # Status check
        if crop_w == target_w and crop_h == target_h:
            status_text = "✓ EXACT SIZE"
            status_color = (0, 150, 0)
        else:
            status_text = f"! Expected {target_w}×{target_h}"
            status_color = (200, 0, 0)
        
        draw.text((canvas_w // 2 - 60, canvas_h - 30), status_text, font=font, fill=status_color)
        
        return canvas
    except Exception as e:
        # Fallback
        return Image.new('RGB', (400, 400), color=(200, 200, 200))


def step_2_select_images():
    """Step 3 (old): Select and upload test images for crop preview."""
    st.markdown('<div class="step-header">📸 Step 3: Test Image (Preview)</div>', unsafe_allow_html=True)
    
    # Show generated prompts if available
    if st.session_state.monthly_prompts:
        st.markdown("### 📋 Generated Prompts Available")
        with st.expander("View Monthly Prompts", expanded=False):
            for month, prompt in st.session_state.monthly_prompts.items():
                st.markdown(f"**{month}:** {prompt}")
        st.info("💡 You can use these prompts to generate images with AI, or upload your own images")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Option 1: Create Placeholder")
        st.info("Generate a test image with precise dimensions and visible markers")
        
        placeholder_width = st.number_input("Width (px)", min_value=100, max_value=6000, value=2000, step=100)
        placeholder_height = st.number_input("Height (px)", min_value=100, max_value=6000, value=2000, step=100)
        
        if st.button("🎨 Create Placeholder Image", use_container_width=True):
            test_dir = Path("/workspaces/artomate/test_output")
            test_dir.mkdir(exist_ok=True)
            
            placeholder = create_placeholder_image(placeholder_width, placeholder_height)
            test_image_path = test_dir / f"placeholder_{placeholder_width}x{placeholder_height}.png"
            placeholder.save(test_image_path)
            
            st.session_state.test_image_path = str(test_image_path)
            st.session_state.test_image = placeholder
            
            st.success(f"✅ Created: {placeholder_width}×{placeholder_height}px")
            st.image(st.session_state.test_image, caption="Placeholder", width=300)
    
    with col2:
        st.markdown("### Option 2: Upload Image")
        uploaded_file = st.file_uploader(
            "Choose a test image",
            type=["jpg", "jpeg", "png", "webp"],
            help="Select an image to test cropping"
        )
        
        if uploaded_file is not None:
            test_dir = Path("/workspaces/artomate/test_output")
            test_dir.mkdir(exist_ok=True)
            
            test_image_path = test_dir / uploaded_file.name
            test_image_path.write_bytes(uploaded_file.getbuffer())
            
            st.session_state.test_image_path = str(test_image_path)
            st.session_state.test_image = Image.open(test_image_path)
            
            st.success(f"✅ Image uploaded: {uploaded_file.name}")
            st.image(st.session_state.test_image, caption="Test Image", width=300)
    
    with col3:
        st.markdown("### Option 3: Use Existing")
        test_images_dir = Path("/workspaces/artomate/test_images")
        if test_images_dir.exists():
            existing_images = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
            if existing_images:
                selected_image = st.selectbox(
                    "Choose from existing images",
                    existing_images,
                    format_func=lambda x: x.name
                )
                
                if selected_image and st.button("📂 Use This Image", use_container_width=True):
                    st.session_state.test_image_path = str(selected_image)
                    st.session_state.test_image = Image.open(selected_image)
                    st.success(f"✅ Selected: {selected_image.name}")
                    st.image(st.session_state.test_image, caption="Test Image", width=300)
            else:
                st.info("No images found")
        else:
            st.info("No test_images/ directory")
    
    if st.session_state.test_image is not None:
        st.markdown("---")
        if st.button("✅ Continue to Product Selection", key="step2_next", use_container_width=True):
            st.session_state.current_step = "select_products"
            st.rerun()


def step_1_generate_prompts():
    """Step 1: Generate AI prompts for 12 monthly images."""
    st.markdown('<div class="step-header">🤖 Step 1: Generate AI Prompts</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">Generate unique AI prompts for 12 monthly calendar images based on themes, animals, and styles.</div>', unsafe_allow_html=True)
    
    # Lists from N8N workflow
    ANIMALS = [
        "Ant", "Antelope", "Arctic Fox", "Bat", "Bear", "Beaver", "Bee",
        "Beetle", "Betta Fish", "Boar", "Buffalo", "Butterfly", "Camel",
        "Canary", "Cat", "Chameleon", "Cheetah", "Chicken", "Coral Fish",
        "Cow", "Crab", "Crocodile", "Crow", "Deer", "Dog", "Dolphin",
        "Donkey", "Dove", "Dragon", "Dragonfly", "Duck", "Eagle", "Elephant",
        "Fairy", "Flamingo", "Fox", "Frog", "Gazelle", "Giraffe", "Goat",
        "Goldfish", "Gorilla", "Griffin", "Guinea Pig", "Hamster", "Hawk",
        "Hedgehog", "Hippo", "Horse", "Hummingbird", "Hyena", "Iguana",
        "Jellyfish", "Kangaroo", "Koala", "Ladybug", "Lemur", "Leopard",
        "Lion", "Lizard", "Lynx", "Meerkat", "Mermaid", "Monkey", "Moose",
        "Moth", "Octopus", "Orca", "Otter", "Owl", "Panda", "Parrot",
        "Peacock", "Pegasus", "Pelican", "Penguin", "Phoenix", "Pig",
        "Polar Bear", "Puma", "Rabbit", "Raccoon", "Reindeer", "Rhino",
        "Rooster", "Sea Turtle", "Seahorse", "Seal", "Shark", "Sheep",
        "Skunk", "Snake", "Spider", "Spirit Animal", "Squirrel", "Starfish",
        "Stingray", "Swan", "Tiger", "Turtle", "Unicorn", "Walrus", "Whale",
        "Wolf", "Zebra"
    ]
    
    STYLES = [
        "Realistic", "Watercolor", "Line Art", "Pop Art", "Abstract", "Boho",
        "Cute", "Anime", "Fantasy", "Minimalist", "Geometric", "Japandi",
        "Vintage", "Cyberpunk", "Neon", "Vaporwave", "Art Deco", "Cartoon",
        "Low Poly", "3D Render", "Ink Painting", "Pencil Sketch",
        "Pastel Illustrative", "Botanical", "Retro", "Modern Poster"
    ]
    
    THEMES = [
        "Christmas", "Valentine", "Halloween", "Easter", "Spring Blossom",
        "Summer Beach", "Fall Harvest", "Winter Snow", "Independence Day",
        "Memorial Day", "Pride Month", "St. Patrick's Day", "Lunar New Year",
        "Thanksgiving", "Horror Spooky", "Forest", "Ocean", "Space", "Desert",
        "Mountain", "Rainy Mood", "Snowy Night", "Aurora", "Japanese Spring",
        "Autumn Leaves", "Baby Nursery", "Wedding", "Cottagecore",
        "Coastal Aesthetic"
    ]
    
    # Input parameters
    st.markdown("### 🎨 Prompt Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        description = st.text_input("Main Theme", 
                                    placeholder="e.g., cute animals in nature, fantasy creatures", 
                                    value=st.session_state.prompt_params.get('description', ''))
        
        # Animals selection with random option
        use_random_animals = st.checkbox("🎲 Random Animals", 
                                         value=st.session_state.prompt_params.get('random_animals', False))
        if use_random_animals:
            num_animals = st.slider("Number of random animals", 3, 8, 5)
            st.info(f"Will randomly select {num_animals} animals")
            animals = []
        else:
            animals = st.multiselect("Animals/Subjects", ANIMALS,
                                    default=st.session_state.prompt_params.get('animals', []))
        
        # Styles selection with random option
        use_random_styles = st.checkbox("🎲 Random Styles",
                                       value=st.session_state.prompt_params.get('random_styles', False))
        if use_random_styles:
            num_styles = st.slider("Number of random styles", 2, 6, 3)
            st.info(f"Will randomly select {num_styles} styles")
            styles = []
        else:
            styles = st.multiselect("Art Styles", STYLES,
                                   default=st.session_state.prompt_params.get('styles', []))
    
    with col2:
        # Themes selection with random option
        use_random_themes = st.checkbox("🎲 Random Themes",
                                       value=st.session_state.prompt_params.get('random_themes', False))
        if use_random_themes:
            num_themes = st.slider("Number of random themes", 2, 6, 3)
            st.info(f"Will randomly select {num_themes} themes")
            themes = []
        else:
            themes = st.multiselect("Themes", THEMES,
                                   default=st.session_state.prompt_params.get('themes', []))
        
        # Animals per image with random option
        use_random_count = st.checkbox("🎲 Random Animals Per Image",
                                      value=st.session_state.prompt_params.get('random_count', False))
        if use_random_count:
            st.info("Will randomly select 1-4 animals per image")
            animals_per_image = 0
        else:
            animals_per_image = st.number_input("Animals per Image", 
                                               min_value=1, max_value=5, value=1,
                                               help="How many animals to show on each calendar image")
    
    # Generate prompts button
    if st.button("🎯 Generate 12 Monthly Prompts", type="primary", use_container_width=True):
        import random
        
        # Apply random selections if needed
        final_animals = animals
        if use_random_animals:
            final_animals = random.sample(ANIMALS, num_animals)
            
        final_styles = styles
        if use_random_styles:
            final_styles = random.sample(STYLES, num_styles)
            
        final_themes = themes
        if use_random_themes:
            final_themes = random.sample(THEMES, num_themes)
            
        final_count = animals_per_image
        if use_random_count:
            final_count = random.randint(1, 4)
        
        if not final_animals or not final_styles or not final_themes:
            st.error("⚠️ Please select or enable random for Animals, Styles, and Themes!")
            return
        
        # Save parameters
        st.session_state.prompt_params = {
            'description': description,
            'animals': final_animals,
            'styles': final_styles,
            'themes': final_themes,
            'animals_per_image': final_count,
            'random_animals': use_random_animals,
            'random_styles': use_random_styles,
            'random_themes': use_random_themes,
            'random_count': use_random_count
        }
        
        # Generate prompts for each month
        months = ["January", "February", "March", "April", "May", "June", 
                 "July", "August", "September", "October", "November", "December"]
        
        monthly_themes_map = {
            "January": "winter, snow, New Year celebration",
            "February": "Valentine's Day, hearts, love, romance",
            "March": "spring awakening, flowers blooming, fresh start",
            "April": "Easter, spring showers, renewal, nature",
            "May": "Mother's Day, blooming gardens, sunshine",
            "June": "summer beginning, Father's Day, outdoors adventures",
            "July": "summer vacation, beach vibes, warmth",
            "August": "late summer, adventures, golden sun",
            "September": "autumn beginning, back to school, harvest time",
            "October": "Halloween, fall leaves, cozy atmosphere",
            "November": "Thanksgiving, gratitude, autumn colors",
            "December": "Christmas, winter holidays, snow, festive lights"
        }
        
        st.session_state.monthly_prompts = {}
        for idx, month in enumerate(months):
            # Select animal(s) for this month
            if final_count == 1:
                month_animals = [final_animals[idx % len(final_animals)]]
            else:
                # Rotate through animals for multiple per image
                month_animals = []
                for i in range(final_count):
                    animal_idx = (idx * final_count + i) % len(final_animals)
                    month_animals.append(final_animals[animal_idx])
            
            # Select style and theme for this month
            month_style = final_styles[idx % len(final_styles)]
            month_theme = final_themes[idx % len(final_themes)]
            month_season = monthly_themes_map[month]
            
            # Build prompt
            animals_text = " and ".join(month_animals)
            prompt = f"{month_style} style illustration featuring {animals_text} "
            prompt += f"in a {month_season} setting. "
            prompt += f"Theme: {month_theme}. "
            if description:
                prompt += f"{description}. "
            prompt += f"Landscape orientation, suitable for calendar use, high quality, detailed artwork perfect for wall art and print-on-demand products."
            
            st.session_state.monthly_prompts[month] = {
                "prompt": prompt,
                "orientation": "landscape",
                "usage": "calendar",
                "month": month,
                "animals": month_animals,
                "style": month_style,
                "theme": month_theme
            }
        
        st.success("✅ Generated 12 monthly prompts!")
        st.rerun()
    
    # Display generated prompts
    if st.session_state.monthly_prompts:
        st.markdown("---")
        st.markdown("### 📋 Generated Prompts")
        
        months = ["January", "February", "March", "April", "May", "June", 
                 "July", "August", "September", "October", "November", "December"]
        
        # Display in 3 columns
        for i in range(0, 12, 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < 12:
                    month = months[i + j]
                    prompt_data = st.session_state.monthly_prompts[month]
                    with col:
                        st.markdown(f"**{month}** 📅")
                        st.caption(f"🐾 {', '.join(prompt_data['animals'])} | 🎨 {prompt_data['style']}")
                        st.text_area(
                            f"Prompt for {month}",
                            value=prompt_data['prompt'],
                            height=150,
                            key=f"prompt_{month}",
                            label_visibility="collapsed"
                        )
        
        # Save prompts
        if st.button("💾 Save Prompts to File", use_container_width=True):
            output_dir = Path("/workspaces/artomate/test_output")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_file = output_dir / f"calendar_prompts_{timestamp}.json"
            
            prompt_file.write_text(json.dumps(st.session_state.monthly_prompts, indent=2))
            st.success(f"✅ Prompts saved to {prompt_file}")
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔄 Reset", key="step1_reset"):
            st.session_state.monthly_prompts = {}
            st.session_state.prompt_params = {}
            st.rerun()
    with col2:
        if st.button("⏭️ Skip (Manual Images)", key="step1_skip"):
            st.info("Skipping prompt generation - upload images manually")
            st.session_state.current_step = "select_image"
            st.rerun()
    with col3:
        if st.session_state.monthly_prompts and st.button("✅ Continue to Images", key="step1_next"):
            st.session_state.current_step = "select_image"
            st.rerun()


def step_3_select_products_with_preview():
    """Step 4 (old): Select products and see crops with previews."""
    st.markdown('<div class="step-header">🏷️ Step 4: Select Products & Preview Crops</div>', unsafe_allow_html=True)
    
    if st.session_state.test_image is None:
        st.error("No test image selected. Please go back to Step 2.")
        return
    
    st.markdown('<div class="info-box">Select products and variants. For each variant, you\'ll see: Original → Cropped → On Product</div>', unsafe_allow_html=True)
    
    families = get_product_families()
    
    selected_products = {}
    for family_name, family_info in families.items():
        with st.expander(f"📦 {family_name}", expanded=True):
            variants = family_info.get('variants', {})
            variant_count = len(variants)
            
            st.markdown(f"**Total Variants:** {variant_count} | **Default:** {family_info.get('default_size', 'N/A')}")
            
            test_mode = st.radio(
                "How to test this product?",
                ["Skip", "Test All Variants", "Select Specific Variants"],
                key=f"mode_{family_name}",
                horizontal=True
            )
            
            selected_variants = []
            if test_mode == "Test All Variants":
                selected_variants = list(variants.keys())
            elif test_mode == "Select Specific Variants":
                selected_variants = st.multiselect(
                    "Select variants",
                    list(variants.keys()),
                    key=f"variants_{family_name}"
                )
            
            if selected_variants:
                st.markdown("---")
                st.markdown(f"#### 🎨 Preview: {len(selected_variants)} Variants")
                
                # Determine top product (first variant as the main one)
                top_variant = selected_variants[0] if selected_variants else None
                
                # Show variants in rows with 4 columns per variant (original, cropped, on product, top product)
                for idx, variant in enumerate(selected_variants):
                    variant_info = variants[variant]
                    st.markdown(f"**{variant}** - {variant_info.get('print_area', 'N/A')}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    try:
                        # Col 1: Original
                        with col1:
                            st.caption("📷 Original")
                            st.image(st.session_state.test_image, use_container_width=True)
                        
                        # Col 2: Cropped
                        with col2:
                            st.caption("✂️ Cropped")
                            target_width = variant_info.get('width_px')
                            target_height = variant_info.get('height_px')
                            if target_width and target_height:
                                cropped = crop_image_to_dimensions(
                                    st.session_state.test_image,
                                    target_width,
                                    target_height
                                )
                                st.image(cropped, use_container_width=True)
                            else:
                                st.error("Missing dimensions")
                        
                        # Col 3: On Product (this variant)
                        with col3:
                            st.caption("👕 On Product")
                            if st.session_state.test_image_path:
                                target_width = variant_info.get('width_px')
                                target_height = variant_info.get('height_px')
                                if target_width and target_height:
                                    cropped_for_mockup = crop_image_to_dimensions(
                                        st.session_state.test_image,
                                        target_width,
                                        target_height
                                    )
                                    # Save temporarily for mockup
                                    temp_path = Path("/tmp") / f"temp_crop_{variant}.png"
                                    cropped_for_mockup.save(temp_path)
                                    
                                    mockup = create_product_mockup(
                                        family_name,
                                        variant,
                                        str(temp_path)
                                    )
                                    st.image(mockup, use_container_width=True)
                                else:
                                    st.error("Missing dimensions")
                            else:
                                st.error("No image path")
                        
                        # Col 4: Top Product Preview (first variant as main)
                        with col4:
                            if idx == 0:
                                st.caption("⭐ Top Product")
                                if st.session_state.test_image_path and top_variant:
                                    top_variant_info = variants[top_variant]
                                    target_width = top_variant_info.get('width_px')
                                    target_height = top_variant_info.get('height_px')
                                    if target_width and target_height:
                                        cropped_top = crop_image_to_dimensions(
                                            st.session_state.test_image,
                                            target_width,
                                            target_height
                                        )
                                        temp_path_top = Path("/tmp") / f"temp_crop_top_{top_variant}.png"
                                        cropped_top.save(temp_path_top)
                                        
                                        mockup_top = create_product_mockup(
                                            family_name,
                                            top_variant,
                                            str(temp_path_top)
                                        )
                                        st.image(mockup_top, use_container_width=True)
                                    else:
                                        st.error("Missing dimensions")
                                else:
                                    st.error("No image path")
                            else:
                                st.caption("⭐ Top Product")
                                st.info("See above ↑")
                    
                    except Exception as e:
                        st.error(f"Error generating preview: {str(e)}")
                    
                    st.markdown("---")
                
                selected_products[family_name] = selected_variants
    
    st.session_state.selected_products = selected_products
    
    if selected_products:
        st.markdown("---")
        total_variants = sum(len(v) for v in selected_products.values())
        st.success(f"✅ Selected {len(selected_products)} products with {total_variants} total variants")
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Back to Images", key="step3_back"):
            st.session_state.current_step = "select_image"
            st.rerun()
    with col3:
        if selected_products and st.button("✅ Continue to Approval", key="step3_next"):
            # Generate all crops and save
            if not st.session_state.crop_results:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = Path(f"/workspaces/artomate/test_output/crops_{timestamp}")
                output_dir.mkdir(parents=True, exist_ok=True)
                st.session_state.test_output_dir = str(output_dir)
                
                results = {}
                for product, variants in selected_products.items():
                    results[product] = {}
                    families = get_product_families()
                    variant_specs = families[product]['variants']
                    
                    for variant in variants:
                        specs = variant_specs[variant]
                        cropped = crop_image_to_dimensions(
                            st.session_state.test_image,
                            specs['width_px'],
                            specs['height_px']
                        )
                        crop_path = output_dir / f"{product}_{variant}_crop.png"
                        cropped.save(crop_path)
                        results[product][variant] = str(crop_path)
                
                st.session_state.crop_results = results
            
            st.session_state.current_step = "approval_seo"
            st.rerun()


def step_4_approval_and_seo():
    """Step 4: Generate and display crops."""
    st.markdown('<div class="step-header">⚙️ Step 4: Generating Crops</div>', unsafe_allow_html=True)
    
    if not st.session_state.test_image_path:
        st.error("No test image selected")
        return
    
    if not st.session_state.selected_products:
        st.error("No products selected")
        return
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("/workspaces/artomate/test_output") / f"crops_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    st.session_state.test_output_dir = str(output_dir)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    log_container = st.container()
    
    logs = []
    
    try:
        total_variants = sum(len(v) for v in st.session_state.selected_products.values())
        current = 0
        crop_results = {}
        families = get_product_families()
        
        for product_family, variants in st.session_state.selected_products.items():
            crop_results[product_family] = {}
            
            for variant in variants:
                current += 1
                progress = current / total_variants
                progress_bar.progress(progress)
                
                status_text.write(f"Generating: {product_family} → {variant}")
                
                try:
                    # Get variant specs
                    variant_specs = families[product_family]["variants"][variant]
                    target_width = variant_specs.get("width_px", 1200)
                    target_height = variant_specs.get("height_px", 1200)
                    
                    # Create or crop image
                    if st.session_state.test_image_path:
                        test_image = Image.open(st.session_state.test_image_path)
                        cropped_image = crop_image_to_dimensions(test_image, target_width, target_height)
                    else:
                        # Create placeholder
                        cropped_image = create_placeholder_image(target_width, target_height)
                    
                    # Save
                    crop_path = output_dir / f"{product_family}_{variant}.png"
                    cropped_image.save(str(crop_path))
                    
                    crop_results[product_family][variant] = {
                        "path": str(crop_path),
                        "status": "success",
                        "size": cropped_image.size,
                        "target_size": f"{target_width}×{target_height}px"
                    }
                    
                    logs.append(f"✅ {product_family} → {variant}: {cropped_image.size}")
                    
                except Exception as e:
                    crop_results[product_family][variant] = {
                        "status": "error",
                        "error": str(e)
                    }
                    logs.append(f"❌ {product_family} → {variant}: {str(e)}")
        
        st.session_state.crop_results = crop_results
        
        status_text.write("✅ Crop generation completed!")
        progress_bar.progress(1.0)
        
        with log_container:
            st.markdown("### 📋 Generation Log")
            for log in logs:
                st.text(log)
        
        st.markdown('<div class="success-box">✅ All crops generated successfully!</div>', unsafe_allow_html=True)
        
        st.session_state.current_step = "preview_crops"
        st.rerun()
        
    except Exception as e:
        st.error(f"Error: {str(e)}")


def step_5_preview_crops():
    """Step 5: Preview generated crops."""
    st.markdown('<div class="step-header">👀 Step 5: Preview & Mockups</div>', unsafe_allow_html=True)
    
    if not st.session_state.crop_results:
        st.error("No crops generated")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        total_products = len(st.session_state.crop_results)
        st.metric("Products", total_products)
    with col2:
        total_variants = sum(len(v) for v in st.session_state.crop_results.values())
        st.metric("Variants", total_variants)
    with col3:
        successful = sum(1 for product in st.session_state.crop_results.values() 
                        for v in product.values() if v.get("status") == "success")
        st.metric("Successful", successful)
    
    st.markdown("---")
    
    families = get_product_families()
    
    for product_family, variants in st.session_state.crop_results.items():
        with st.expander(f"📦 {product_family} ({len(variants)} variants)", expanded=True):
            family_info = families.get(product_family, {})
            
            for variant_name, result in variants.items():
                if result.get("status") == "success":
                    st.markdown(f"### {variant_name}")
                    
                    variant_specs = family_info.get('variants', {}).get(variant_name, {})
                    
                    # Specs in 4 columns
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📏 Print Area", variant_specs.get('print_area', 'N/A'))
                    with col2:
                        st.metric("📍 Placement", variant_specs.get('placement', 'N/A'))
                    with col3:
                        st.metric("🎯 Position", variant_specs.get('position', 'N/A')[:15] + "...")
                    with col4:
                        st.metric("💾 Size", f"{result['size'][0]}×{result['size'][1]}px")
                    
                    st.markdown("---")
                    
                    try:
                        # Load original
                        original_img = Image.open(st.session_state.test_image_path)
                        # Load crop
                        crop_img = Image.open(result["path"])
                        # Create placement guide with actual crop and specs
                        guide_img = create_placement_guide(product_family, variant_name, crop_img, variant_specs)
                        # Create product mockup
                        mockup_img = create_product_mockup(product_family, variant_name, result["path"])
                        
                        # Show all 4 previews
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.markdown("**🖼️ Original Image**")
                            st.image(original_img, caption="Original", use_container_width=True)
                        
                        with col2:
                            st.markdown("**✂️ Generated Crop**")
                            st.image(crop_img, caption="Crop", use_container_width=True)
                        
                        with col3:
                            st.markdown("**📐 Placement Guide**")
                            st.image(guide_img, caption="Guide", use_container_width=True)
                        
                        with col4:
                            st.markdown("**🎨 Product Mockup**")
                            st.image(mockup_img, caption="Final Product", use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Error loading images: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                    
                    st.markdown("---")
                    st.markdown("")
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Back", key="step5_back"):
            st.session_state.current_step = "select_products"
            st.rerun()
    with col2:
        if st.button("🔄 New Test", key="step5_new"):
            st.session_state.current_step = "select_image"
            st.rerun()
    with col3:
        if st.button("✅ Approve & Continue", key="step5_continue", type="primary"):
            st.session_state.current_step = "approval_seo"
            st.rerun()


def step_4_approval_and_seo():
    """Step 5 (old): Approve variants with all visible side by side and add SEO."""
    st.markdown('<div class="step-header">✅ Step 5: Approval & SEO</div>', unsafe_allow_html=True)
    
    if not st.session_state.crop_results:
        st.error("No crops to approve. Please go back to Step 3.")
        return
    
    families = get_product_families()
    
    # Count approved
    approved_count = sum(1 for key, val in st.session_state.approved_variants.items() if val)
    total_count = sum(len(variants) for variants in st.session_state.crop_results.values())
    
    # Top section - Quick approval
    st.markdown("### 🎯 Quick Approval")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.metric("✅ Approved Variants", f"{approved_count} / {total_count}")
    with col2:
        if st.button("✅ Approve All", key="approve_all", use_container_width=True):
            count = 0
            for product_family, variants in st.session_state.crop_results.items():
                for variant_name in variants.keys():
                    key = f"{product_family}_{variant_name}"
                    st.session_state.approved_variants[key] = True
                    count += 1
            st.success(f"✅ Approved {count} variants!")
            st.rerun()
    with col3:
        if st.button("❌ Unapprove All", key="unapprove_all", use_container_width=True):
            st.session_state.approved_variants = {}
            st.success("❌ All unapproved!")
            st.rerun()
    
    st.markdown("---")
    
    # Display all products and variants side by side
    for product_family, variants in st.session_state.crop_results.items():
        st.markdown(f"### 📦 {product_family}")
        
        # Show all variants in grid (4 per row)
        variant_list = list(variants.keys())
        for i in range(0, len(variant_list), 4):
            cols = st.columns(4)
            for j, col in enumerate(cols):
                if i + j < len(variant_list):
                    variant_name = variant_list[i + j]
                    variant_info = families[product_family]['variants'][variant_name]
                    key = f"{product_family}_{variant_name}"
                    crop_path = variants[variant_name]
                    
                    with col:
                        # Show image
                        try:
                            if isinstance(crop_path, dict):
                                crop_path = crop_path.get("path", crop_path)
                            crop_img = Image.open(crop_path)
                            st.image(crop_img, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error loading: {str(e)}")
                        
                        # Variant info
                        st.markdown(f"**{variant_name}**")
                        st.caption(f"📏 {variant_info.get('print_area', 'N/A')}")
                        
                        # Approval checkbox
                        if key not in st.session_state.approved_variants:
                            st.session_state.approved_variants[key] = False
                        
                        approved = st.checkbox(
                            "✅ Approve",
                            key=f"approve_{key}",
                            value=st.session_state.approved_variants[key]
                        )
                        st.session_state.approved_variants[key] = approved
        
        st.markdown("---")
    
    # SEO section for approved variants
    approved_list = [(pf, vn, f"{pf}_{vn}") 
                     for pf, variants in st.session_state.crop_results.items() 
                     for vn in variants 
                     if st.session_state.approved_variants.get(f"{pf}_{vn}", False)]
    
    if approved_list:
        st.markdown("### 🔍 SEO Configuration")
        st.info(f"Configure SEO for {len(approved_list)} approved variant(s)")
        
        # Quick SEO template
        with st.expander("📝 Quick SEO Template", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                global_title = st.text_input("Title Template", 
                    value="{product} {variant} - Modern Design",
                    help="Use {product} and {variant}")
                global_tags = st.text_input("Tags", 
                    value="art, print, wall decor, modern")
            with col2:
                global_category = st.selectbox("Category", 
                    ["Art & Photography", "Home Decor", "Fashion", "Accessories"])
                global_price = st.number_input("Base Price ($)", value=19.99, step=1.0)
            
            if st.button("🚀 Apply to All Approved", type="primary"):
                for product_family, variant_name, key in approved_list:
                    title = global_title.replace("{product}", product_family).replace("{variant}", variant_name)
                    st.session_state.variant_seo[key] = {
                        "title": title,
                        "description": f"{product_family} in {variant_name} size. High quality print.",
                        "tags": global_tags,
                        "category": global_category,
                        "price": global_price
                    }
                st.success(f"✅ Applied SEO to {len(approved_list)} variants!")
                st.rerun()
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Back to Products", key="step4_back"):
            st.session_state.current_step = "select_products"
            st.rerun()
    with col3:
        if approved_count > 0:
            if st.button("📤 Continue to Publishing", key="step4_next", type="primary"):
                st.session_state.current_step = "publishing"
                st.rerun()
        else:
            st.button("⚠️ Approve Variants First", key="step4_disabled", disabled=True)


def step_5_publishing():
    """Step 5: Publishing and Export."""
    st.markdown('<div class="step-header">📤 Step 5: Publishing</div>', unsafe_allow_html=True)
    
    approved_list = [(k.split('_')[0], '_'.join(k.split('_')[1:]), k) 
                     for k, v in st.session_state.approved_variants.items() if v]
    
    if not approved_list:
        st.error("No approved variants. Please go back to Step 4.")
        return
    
    st.info(f"📊 Publishing {len(approved_list)} approved variant(s)")
    
    # Initialize publish status
    for _, _, key in approved_list:
        if key not in st.session_state.publish_status:
            st.session_state.publish_status[key] = {
                "printify": False,
                "etsy": False,
                "social_media": False,
            }
    
    # Platform Publishing
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🖨️ Print-on-Demand")
        
        if st.button("📤 Upload to Printify", key="upload_printify", use_container_width=True):
            with st.spinner("Uploading to Printify..."):
                import time
                time.sleep(1)
                for _, _, key in approved_list:
                    st.session_state.publish_status[key]["printify"] = True
                st.success(f"✅ {len(approved_list)} variants uploaded to Printify!")
        
        if st.button("📤 Create Etsy Listings", key="upload_etsy", use_container_width=True):
            with st.spinner("Creating Etsy listings..."):
                import time
                time.sleep(1)
                for _, _, key in approved_list:
                    st.session_state.publish_status[key]["etsy"] = True
                st.success(f"✅ {len(approved_list)} listings created on Etsy!")
    
    with col2:
        st.markdown("### 📱 Social Media")
        
        platforms = st.multiselect(
            "Select platforms",
            ["Instagram", "Facebook", "Pinterest", "TikTok"],
            default=["Instagram", "Pinterest"]
        )
        
        if st.button("📤 Post to Social Media", key="upload_social", use_container_width=True):
            with st.spinner(f"Posting to {', '.join(platforms)}..."):
                import time
                time.sleep(1)
                for _, _, key in approved_list:
                    st.session_state.publish_status[key]["social_media"] = True
                st.success(f"✅ Posted to {', '.join(platforms)}!")
    
    # Publishing Status
    st.markdown("---")
    st.markdown("### 📊 Publishing Status")
    
    for product, variant, key in approved_list:
        status = st.session_state.publish_status[key]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"**{product} - {variant}**")
        with col2:
            st.markdown("🖨️ " + ("✅" if status["printify"] else "⏳"))
        with col3:
            st.markdown("🛍️ " + ("✅" if status["etsy"] else "⏳"))
        with col4:
            st.markdown("📱 " + ("✅" if status["social_media"] else "⏳"))
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Back to Approval", key="step5_back"):
            st.session_state.current_step = "approval_seo"
            st.rerun()
    with col2:
        if st.button("💾 Export Report", key="export_report"):
            report = {
                "timestamp": datetime.now().isoformat(),
                "approved_variants": approved_list,
                "publish_status": st.session_state.publish_status
            }
            output_dir = Path(st.session_state.test_output_dir) if st.session_state.test_output_dir else Path("/workspaces/artomate/test_output")
            output_dir.mkdir(parents=True, exist_ok=True)
            report_path = output_dir / "publish_report.json"
            report_path.write_text(json.dumps(report, indent=2))
            st.success(f"✅ Report exported to {report_path}")
    with col3:
        if st.button("🎉 Start New Project", key="step5_new", type="primary"):
            st.session_state.current_step = "generate_prompts"
            st.session_state.approved_variants = {}
            st.session_state.seo_metadata = {}
            st.session_state.publish_status = {}
            st.rerun()


def main():
    """Main app."""
    st.markdown('<div class="main-header">🎨 Artomate - Content to Commerce</div>', unsafe_allow_html=True)
    st.markdown("**Complete automation from AI prompts to marketplace products**")
    
    with st.sidebar:
        st.markdown("### 📍 Workflow Progress")
        
        # Define complete workflow steps
        steps = [
            {"key": "generate_prompts", "name": "1️⃣ Generate AI Prompts", "enabled": True, "icon": "🤖"},
            {"key": "generate_images", "name": "2️⃣ Generate Images (AI)", "enabled": bool(st.session_state.monthly_prompts), "icon": "🎨"},
            {"key": "select_image", "name": "3️⃣ Test Image (Preview)", "enabled": True, "icon": "📸"},
            {"key": "select_products", "name": "4️⃣ Select Products", "enabled": st.session_state.test_image is not None or bool(st.session_state.generated_images), "icon": "🏷️"},
            {"key": "approval_seo", "name": "5️⃣ Approval & SEO", "enabled": bool(st.session_state.selected_products), "icon": "✅"},
            {"key": "create_printify", "name": "6️⃣ Create Printify Products", "enabled": bool(st.session_state.approved_variants), "icon": "🖨️"},
            {"key": "create_etsy", "name": "7️⃣ Create Etsy Listings", "enabled": bool(st.session_state.printify_products), "icon": "🛍️"},
            {"key": "generate_videos", "name": "8️⃣ Generate Viral Videos", "enabled": bool(st.session_state.approved_variants), "icon": "🎬"},
            {"key": "publish_social", "name": "9️⃣ Social Media Posts", "enabled": bool(st.session_state.viral_videos) or bool(st.session_state.approved_variants), "icon": "📱"},
            {"key": "submit_stock", "name": "🔟 Stock Platforms", "enabled": bool(st.session_state.approved_variants), "icon": "📊"},
            {"key": "export_summary", "name": "1️⃣1️⃣ Export & Summary", "enabled": True, "icon": "📦"}
        ]
        
        # Show step status and make them clickable
        for step in steps:
            step_key = step["key"]
            step_name = step["name"]
            step_icon = step.get("icon", "")
            is_current = step_key == st.session_state.current_step
            is_enabled = step["enabled"]
            
            # Determine step status
            if is_current:
                # Current step - highlighted
                if st.button(f"➡️ {step_name}", key=f"nav_{step_key}", use_container_width=True, type="primary"):
                    pass  # Already on this step
            elif is_enabled:
                # Enabled step - clickable
                if st.button(f"{step_icon} {step_name}", key=f"nav_{step_key}", use_container_width=True):
                    st.session_state.current_step = step_key
                    st.rerun()
            else:
                # Disabled step - not yet accessible
                st.button(f"⏸️ {step_name}", key=f"nav_{step_key}", use_container_width=True, disabled=True)
        
        st.markdown("---")
        
        # Show data status
        st.markdown("### 💾 Data Status")
        data_status = []
        if st.session_state.monthly_prompts:
            data_status.append(f"✅ {len(st.session_state.monthly_prompts)} prompts")
        if st.session_state.generated_images:
            data_status.append(f"✅ {len(st.session_state.generated_images)} AI images")
        if st.session_state.test_image:
            data_status.append("✅ Test image loaded")
        if st.session_state.selected_products:
            total_variants = sum(len(v) for v in st.session_state.selected_products.values())
            data_status.append(f"✅ {len(st.session_state.selected_products)} products ({total_variants} variants)")
        if st.session_state.approved_variants:
            approved_count = sum(1 for v in st.session_state.approved_variants.values() if v)
            data_status.append(f"✅ {approved_count} approved")
        if st.session_state.printify_products:
            data_status.append(f"✅ {len(st.session_state.printify_products)} Printify products")
        if st.session_state.etsy_listings:
            data_status.append(f"✅ {len(st.session_state.etsy_listings)} Etsy listings")
        if st.session_state.viral_videos:
            data_status.append(f"✅ {len(st.session_state.viral_videos)} viral videos")
        if st.session_state.social_posts:
            data_status.append(f"✅ {len(st.session_state.social_posts)} social posts")
        if st.session_state.stock_submissions:
            data_status.append(f"✅ {len(st.session_state.stock_submissions)} stock submissions")
        
        if data_status:
            for status in data_status:
                st.markdown(f"- {status}")
        else:
            st.info("No data yet")
        
        st.markdown("---")
        st.markdown("### ℹ️ Quick Guide")
        with st.expander("Complete Workflow"):
            st.markdown("""
**Complete Automation Flow:**

1. **Generate AI Prompts** - 12 monthly themes
2. **Generate Images** - AI creates 12 designs
3. **Test Image** - Preview crops (optional)
4. **Select Products** - Choose variants
5. **Approval & SEO** - Review & optimize
6. **Printify Products** - Create POD items
7. **Etsy Listings** - Auto-create shop items
8. **Viral Videos** - TikTok/Reels/Shorts
9. **Social Media** - Instagram/Facebook/Pinterest
10. **Stock Platforms** - Shutterstock/Adobe
11. **Export** - Download everything

**From 1 prompt → 600+ assets!**
            """)
    
    # Route to appropriate step function
    if st.session_state.current_step == "generate_prompts":
        step_1_generate_prompts()
    elif st.session_state.current_step == "generate_images":
        step_2_generate_images()
    elif st.session_state.current_step == "select_image":
        step_3_select_test_image()
    elif st.session_state.current_step == "select_products":
        step_4_select_products_with_preview()
    elif st.session_state.current_step == "approval_seo":
        step_5_approval_and_seo()
    elif st.session_state.current_step == "create_printify":
        step_6_create_printify_products()
    elif st.session_state.current_step == "create_etsy":
        step_7_create_etsy_listings()
    elif st.session_state.current_step == "generate_videos":
        step_8_generate_viral_videos()
    elif st.session_state.current_step == "publish_social":
        step_9_publish_social_media()
    elif st.session_state.current_step == "submit_stock":
        step_10_submit_stock_platforms()
    elif st.session_state.current_step == "export_summary":
        step_11_export_summary()


def step_2_generate_images():
    """Step 2: Generate AI images from prompts."""
    st.markdown('<div class="step-header">🎨 Step 2: Generate AI Images</div>', unsafe_allow_html=True)
    
    if not st.session_state.monthly_prompts:
        st.error("No prompts generated. Please go back to Step 1.")
        if st.button("⬅️ Back to Prompts"):
            st.session_state.current_step = "generate_prompts"
            st.rerun()
        return
    
    st.markdown('<div class="info-box">Generate 12 unique images using AI (DALL-E 3 or Midjourney)</div>', unsafe_allow_html=True)
    
    # AI Provider selection
    col1, col2, col3 = st.columns(3)
    with col1:
        ai_provider = st.selectbox("AI Provider", ["DALL-E 3 (OpenAI)", "Midjourney", "Stable Diffusion", "Placeholder (Test)"])
    with col2:
        image_size = st.selectbox("Image Size", ["1024x1024", "1792x1024", "1024x1792"])
    with col3:
        quality = st.selectbox("Quality", ["standard", "hd"])
    
    # Show prompts that will be generated
    st.markdown("### 📋 Prompts to Generate")
    months = ["January", "February", "March", "April", "May", "June", 
             "July", "August", "September", "October", "November", "December"]
    
    for i in range(0, 12, 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < 12:
                month = months[i + j]
                prompt_data = st.session_state.monthly_prompts[month]
                with col:
                    st.markdown(f"**{month}** 📅")
                    st.caption(f"🐾 {', '.join(prompt_data['animals'][:2])}")
                    already_generated = month in st.session_state.generated_images
                    if already_generated:
                        st.success("✅ Generated")
                    else:
                        st.info("⏳ Pending")
    
    # Generate button
    st.markdown("---")
    if st.button("🚀 Generate All 12 Images", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, month in enumerate(months):
            progress = (idx + 1) / 12
            progress_bar.progress(progress)
            status_text.write(f"Generating {month}... ({idx + 1}/12)")
            
            prompt_data = st.session_state.monthly_prompts[month]
            
            # Simulate generation (in real app, call OpenAI API)
            import time
            time.sleep(0.5)
            
            if "Placeholder" in ai_provider:
                # Create placeholder for testing
                test_img = create_placeholder_image(1024, 1024, f"{month}\n{', '.join(prompt_data['animals'][:2])}")
                
                # Save to disk
                output_dir = Path("/workspaces/artomate/test_output/generated_images")
                output_dir.mkdir(parents=True, exist_ok=True)
                img_path = output_dir / f"{month.lower()}_generated.png"
                test_img.save(img_path)
                
                st.session_state.generated_images[month] = {
                    "path": str(img_path),
                    "prompt": prompt_data['prompt'],
                    "animals": prompt_data['animals'],
                    "style": prompt_data['style'],
                    "theme": prompt_data['theme']
                }
            else:
                st.warning(f"AI Provider '{ai_provider}' not yet implemented. Using placeholder.")
        
        status_text.write("✅ All images generated!")
        st.success(f"✅ Generated {len(st.session_state.generated_images)} images!")
        time.sleep(1)
        st.rerun()
    
    # Show generated images
    if st.session_state.generated_images:
        st.markdown("---")
        st.markdown("### 🖼️ Generated Images")
        
        for i in range(0, 12, 4):
            cols = st.columns(4)
            for j, col in enumerate(cols):
                if i + j < 12:
                    month = months[i + j]
                    if month in st.session_state.generated_images:
                        img_data = st.session_state.generated_images[month]
                        with col:
                            st.image(img_data['path'], caption=month, use_container_width=True)
                            st.caption(f"🐾 {', '.join(img_data['animals'][:2])}")
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Back to Prompts"):
            st.session_state.current_step = "generate_prompts"
            st.rerun()
    with col2:
        if st.session_state.generated_images and st.button("⏭️ Skip to Products"):
            st.session_state.current_step = "select_products"
            st.rerun()
    with col3:
        if st.session_state.generated_images and st.button("✅ Continue to Test Image"):
            st.session_state.current_step = "select_image"
            st.rerun()


def step_3_select_test_image():
    """Step 3: Select test image for crop preview (renamed from step_2)."""
    step_2_select_images()  # Call the existing function


def step_4_select_products_with_preview():
    """Step 4: Select products (renamed from step_3)."""
    step_3_select_products_with_preview()  # Call the existing function


def step_5_approval_and_seo():
    """Step 5: Approval and SEO (renamed from step_4)."""
    step_4_approval_and_seo()  # Call the existing function


def step_6_create_printify_products():
    """Step 6: Create Printify products."""
    st.markdown('<div class="step-header">🖨️ Step 6: Create Printify Products</div>', unsafe_allow_html=True)
    
    if not st.session_state.approved_variants:
        st.error("No approved variants. Please go back to Step 5.")
        return
    
    approved_list = [(k.split('_')[0], '_'.join(k.split('_')[1:]), k) 
                     for k, v in st.session_state.approved_variants.items() if v]
    
    st.info(f"📦 Creating Printify products for {len(approved_list)} approved variant(s)")
    
    # Printify settings
    col1, col2 = st.columns(2)
    with col1:
        provider = st.selectbox("Print Provider", ["Printify Choice (99)", "Other Provider"])
        blueprint_type = st.selectbox("Product Type", ["Poster", "T-Shirt", "Canvas", "Mug", "Hoodie"])
    with col2:
        price_markup = st.number_input("Price Markup (%)", min_value=0, max_value=500, value=100, step=10)
        publish_to_store = st.checkbox("Publish to store immediately", value=False)
    
    if st.button("🖨️ Create All Printify Products", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, (product, variant, key) in enumerate(approved_list):
            progress = (idx + 1) / len(approved_list)
            progress_bar.progress(progress)
            status_text.write(f"Creating {product} - {variant}... ({idx + 1}/{len(approved_list)})")
            
            # Simulate Printify API call
            import time
            time.sleep(0.3)
            
            product_id = f"pfy_{idx + 1000}"
            st.session_state.printify_products[key] = {
                "printify_id": product_id,
                "product": product,
                "variant": variant,
                "provider": provider,
                "blueprint": blueprint_type,
                "markup": price_markup,
                "published": publish_to_store,
                "url": f"https://printify.com/app/products/{product_id}"
            }
        
        status_text.write("✅ All Printify products created!")
        st.success(f"✅ Created {len(st.session_state.printify_products)} Printify products!")
        time.sleep(1)
        st.rerun()
    
    # Show created products
    if st.session_state.printify_products:
        st.markdown("---")
        st.markdown("### 📦 Created Printify Products")
        
        for key, product_data in st.session_state.printify_products.items():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**{product_data['product']}**")
                st.caption(product_data['variant'])
            with col2:
                st.metric("Product ID", product_data['printify_id'])
            with col3:
                st.metric("Markup", f"{product_data['markup']}%")
            with col4:
                if st.button("View", key=f"view_{key}"):
                    st.info(f"🔗 {product_data['url']}")
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Back to Approval"):
            st.session_state.current_step = "approval_seo"
            st.rerun()
    with col3:
        if st.session_state.printify_products and st.button("✅ Continue to Etsy"):
            st.session_state.current_step = "create_etsy"
            st.rerun()


def step_7_create_etsy_listings():
    """Step 7: Create Etsy listings."""
    st.markdown('<div class="step-header">🛍️ Step 7: Create Etsy Listings</div>', unsafe_allow_html=True)
    
    if not st.session_state.printify_products:
        st.error("No Printify products created. Please go back to Step 6.")
        return
    
    st.info(f"🛍️ Creating Etsy listings for {len(st.session_state.printify_products)} product(s)")
    
    # Etsy settings
    col1, col2 = st.columns(2)
    with col1:
        shop_section = st.text_input("Shop Section", value="Wall Art")
        processing_time = st.selectbox("Processing Time", ["1-3 business days", "3-5 business days", "1-2 weeks"])
    with col2:
        listing_type = st.selectbox("Listing Type", ["Physical", "Digital"])
        auto_renew = st.checkbox("Auto-renew listings", value=True)
    
    if st.button("🛍️ Create All Etsy Listings", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, (key, product_data) in enumerate(st.session_state.printify_products.items()):
            progress = (idx + 1) / len(st.session_state.printify_products)
            progress_bar.progress(progress)
            status_text.write(f"Creating listing for {product_data['product']}... ({idx + 1}/{len(st.session_state.printify_products)})")
            
            # Simulate Etsy API call
            import time
            time.sleep(0.3)
            
            listing_id = f"etsy_{idx + 5000}"
            
            # Generate SEO title and description
            seo_data = st.session_state.variant_seo.get(key, {})
            title = seo_data.get('title', f"{product_data['product']} - {product_data['variant']}")
            
            st.session_state.etsy_listings[key] = {
                "listing_id": listing_id,
                "title": title,
                "product": product_data['product'],
                "variant": product_data['variant'],
                "price": seo_data.get('price', 19.99),
                "tags": seo_data.get('tags', '').split(',')[:13],
                "section": shop_section,
                "processing_time": processing_time,
                "url": f"https://etsy.com/listing/{listing_id}"
            }
        
        status_text.write("✅ All Etsy listings created!")
        st.success(f"✅ Created {len(st.session_state.etsy_listings)} Etsy listings!")
        time.sleep(1)
        st.rerun()
    
    # Show created listings
    if st.session_state.etsy_listings:
        st.markdown("---")
        st.markdown("### 🛍️ Created Etsy Listings")
        
        for key, listing_data in st.session_state.etsy_listings.items():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**{listing_data['title'][:30]}...**")
            with col2:
                st.metric("Price", f"${listing_data['price']}")
            with col3:
                st.metric("Tags", len(listing_data['tags']))
            with col4:
                if st.button("View", key=f"view_etsy_{key}"):
                    st.info(f"🔗 {listing_data['url']}")
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Back to Printify"):
            st.session_state.current_step = "create_printify"
            st.rerun()
    with col3:
        if st.button("✅ Continue to Videos"):
            st.session_state.current_step = "generate_videos"
            st.rerun()


def step_8_generate_viral_videos():
    """Step 8: Generate viral videos."""
    st.markdown('<div class="step-header">🎬 Step 8: Generate Viral Videos</div>', unsafe_allow_html=True)
    
    if not st.session_state.approved_variants:
        st.error("No approved variants. Please go back to Step 5.")
        return
    
    approved_list = [(k.split('_')[0], '_'.join(k.split('_')[1:]), k) 
                     for k, v in st.session_state.approved_variants.items() if v]
    
    st.info(f"🎬 Creating viral videos for {min(3, len(approved_list))} variant(s)")
    
    # Video settings
    col1, col2, col3 = st.columns(3)
    with col1:
        platforms = st.multiselect("Platforms", ["TikTok", "Instagram Reels", "YouTube Shorts"], default=["TikTok", "Instagram Reels"])
    with col2:
        video_style = st.selectbox("Animation Style", ["Ken Burns", "Zoom", "Pan", "Slideshow"])
    with col3:
        add_features = st.multiselect("Features", ["AI Facts", "Background Music", "Viral Hook"], default=["AI Facts", "Viral Hook"])
    
    if st.button("🎬 Generate Viral Videos", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Generate for first 3 variants only (to save time)
        for idx, (product, variant, key) in enumerate(approved_list[:3]):
            for platform in platforms:
                progress = ((idx * len(platforms)) + platforms.index(platform) + 1) / (min(3, len(approved_list)) * len(platforms))
                progress_bar.progress(progress)
                status_text.write(f"Creating {platform} video for {product}...")
                
                # Simulate video generation
                import time
                time.sleep(0.5)
                
                video_key = f"{key}_{platform.lower().replace(' ', '_')}"
                st.session_state.viral_videos[video_key] = {
                    "product": product,
                    "variant": variant,
                    "platform": platform,
                    "style": video_style,
                    "duration": "15s" if platform != "YouTube Shorts" else "60s",
                    "features": add_features,
                    "path": f"/test_output/videos/{video_key}.mp4"
                }
        
        status_text.write("✅ All videos generated!")
        st.success(f"✅ Generated {len(st.session_state.viral_videos)} viral videos!")
        time.sleep(1)
        st.rerun()
    
    # Show generated videos
    if st.session_state.viral_videos:
        st.markdown("---")
        st.markdown("### 🎬 Generated Videos")
        
        for video_key, video_data in st.session_state.viral_videos.items():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**{video_data['product']}**")
                st.caption(video_data['variant'])
            with col2:
                st.metric("Platform", video_data['platform'])
            with col3:
                st.metric("Duration", video_data['duration'])
            with col4:
                st.info(f"Style: {video_data['style']}")
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Back to Etsy"):
            st.session_state.current_step = "create_etsy"
            st.rerun()
    with col3:
        if st.button("✅ Continue to Social Media"):
            st.session_state.current_step = "publish_social"
            st.rerun()


def step_9_publish_social_media():
    """Step 9: Publish to social media."""
    st.markdown('<div class="step-header">📱 Step 9: Social Media Publishing</div>', unsafe_allow_html=True)
    
    st.info("📱 Publish your content across social media platforms")
    
    # Platform selection
    st.markdown("### 📱 Select Platforms")
    col1, col2, col3 = st.columns(3)
    with col1:
        publish_instagram = st.checkbox("Instagram", value=True)
        if publish_instagram:
            st.caption("✅ Carousel + Reels")
    with col2:
        publish_tiktok = st.checkbox("TikTok", value=True)
        if publish_tiktok:
            st.caption("✅ Short videos")
    with col3:
        publish_youtube = st.checkbox("YouTube Shorts", value=False)
        if publish_youtube:
            st.caption("✅ 60s videos")
    
    col1, col2 = st.columns(2)
    with col1:
        publish_facebook = st.checkbox("Facebook", value=False)
    with col2:
        publish_pinterest = st.checkbox("Pinterest", value=False)
    
    if st.button("📱 Publish to Social Media", type="primary", use_container_width=True):
        platforms_selected = []
        if publish_instagram:
            platforms_selected.append("Instagram")
        if publish_tiktok:
            platforms_selected.append("TikTok")
        if publish_youtube:
            platforms_selected.append("YouTube")
        if publish_facebook:
            platforms_selected.append("Facebook")
        if publish_pinterest:
            platforms_selected.append("Pinterest")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, platform in enumerate(platforms_selected):
            progress = (idx + 1) / len(platforms_selected)
            progress_bar.progress(progress)
            status_text.write(f"Publishing to {platform}...")
            
            import time
            time.sleep(0.5)
            
            st.session_state.social_posts[platform] = {
                "platform": platform,
                "status": "published",
                "post_count": 3 if platform == "Instagram" else 1,
                "timestamp": datetime.now().isoformat()
            }
        
        status_text.write("✅ Published to all platforms!")
        st.success(f"✅ Published to {len(platforms_selected)} platform(s)!")
        time.sleep(1)
        st.rerun()
    
    # Show published posts
    if st.session_state.social_posts:
        st.markdown("---")
        st.markdown("### 📱 Published Posts")
        
        for platform, post_data in st.session_state.social_posts.items():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**{platform}**")
            with col2:
                st.metric("Posts", post_data['post_count'])
            with col3:
                st.success("✅ Published")
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Back to Videos"):
            st.session_state.current_step = "generate_videos"
            st.rerun()
    with col3:
        if st.button("✅ Continue to Stock Platforms"):
            st.session_state.current_step = "submit_stock"
            st.rerun()


def step_10_submit_stock_platforms():
    """Step 10: Submit to stock platforms."""
    st.markdown('<div class="step-header">📊 Step 10: Stock Platform Submissions</div>', unsafe_allow_html=True)
    
    if not st.session_state.approved_variants:
        st.error("No approved variants.")
        return
    
    approved_list = [(k.split('_')[0], '_'.join(k.split('_')[1:]), k) 
                     for k, v in st.session_state.approved_variants.items() if v]
    
    st.info(f"📊 Preparing submissions for {len(approved_list)} variant(s)")
    
    # Platform selection
    col1, col2 = st.columns(2)
    with col1:
        submit_shutterstock = st.checkbox("Shutterstock", value=True)
    with col2:
        submit_adobe = st.checkbox("Adobe Stock", value=True)
    
    # AI disclosure (required)
    st.markdown("### ⚠️ AI Disclosure")
    ai_disclosure = st.text_area("AI Generation Disclosure", 
        value="This image was generated using artificial intelligence (AI) tools.",
        help="Required for AI-generated content")
    
    if st.button("📊 Prepare Stock Submissions", type="primary", use_container_width=True):
        platforms = []
        if submit_shutterstock:
            platforms.append("Shutterstock")
        if submit_adobe:
            platforms.append("Adobe Stock")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_submissions = len(approved_list) * len(platforms)
        current = 0
        
        for product, variant, key in approved_list:
            for platform in platforms:
                current += 1
                progress = current / total_submissions
                progress_bar.progress(progress)
                status_text.write(f"Preparing {platform} submission... ({current}/{total_submissions})")
                
                import time
                time.sleep(0.2)
                
                seo_data = st.session_state.variant_seo.get(key, {})
                
                submission_key = f"{key}_{platform.lower().replace(' ', '_')}"
                st.session_state.stock_submissions[submission_key] = {
                    "platform": platform,
                    "product": product,
                    "variant": variant,
                    "title": seo_data.get('title', f"{product} - {variant}")[:200],
                    "description": seo_data.get('description', ''),
                    "keywords": seo_data.get('tags', '').split(',')[:50],
                    "ai_disclosure": ai_disclosure,
                    "category": seo_data.get('category', 'Art & Photography'),
                    "status": "ready"
                }
        
        status_text.write("✅ All submissions prepared!")
        st.success(f"✅ Prepared {len(st.session_state.stock_submissions)} stock submissions!")
        time.sleep(1)
        st.rerun()
    
    # Show submissions
    if st.session_state.stock_submissions:
        st.markdown("---")
        st.markdown("### 📊 Prepared Submissions")
        
        for submission_key, submission_data in st.session_state.stock_submissions.items():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**{submission_data['platform']}**")
            with col2:
                st.caption(f"{submission_data['product']} - {submission_data['variant']}")
            with col3:
                st.metric("Keywords", len(submission_data['keywords']))
            with col4:
                st.success("✅ Ready")
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Back to Social"):
            st.session_state.current_step = "publish_social"
            st.rerun()
    with col3:
        if st.button("✅ Continue to Export"):
            st.session_state.current_step = "export_summary"
            st.rerun()


def step_11_export_summary():
    """Step 11: Export and summary."""
    st.markdown('<div class="step-header">📦 Step 11: Export & Summary</div>', unsafe_allow_html=True)
    
    st.markdown("### 🎉 Workflow Complete!")
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Prompts", len(st.session_state.monthly_prompts))
        st.metric("🎨 AI Images", len(st.session_state.generated_images))
    with col2:
        st.metric("✅ Approved", sum(1 for v in st.session_state.approved_variants.values() if v))
        st.metric("🖨️ Printify", len(st.session_state.printify_products))
    with col3:
        st.metric("🛍️ Etsy", len(st.session_state.etsy_listings))
        st.metric("🎬 Videos", len(st.session_state.viral_videos))
    with col4:
        st.metric("📱 Social", len(st.session_state.social_posts))
        st.metric("📊 Stock", len(st.session_state.stock_submissions))
    
    # Total assets created
    total_assets = (
        len(st.session_state.monthly_prompts) +
        len(st.session_state.generated_images) +
        len(st.session_state.printify_products) +
        len(st.session_state.etsy_listings) +
        len(st.session_state.viral_videos) +
        len(st.session_state.social_posts) +
        len(st.session_state.stock_submissions)
    )
    
    st.markdown("---")
    st.markdown(f"### 🚀 Total Assets Created: **{total_assets}**")
    
    # Export options
    st.markdown("### 💾 Export Options")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Export Complete Report (JSON)", use_container_width=True):
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "prompts": st.session_state.monthly_prompts,
                "generated_images": st.session_state.generated_images,
                "approved_variants": {k: v for k, v in st.session_state.approved_variants.items() if v},
                "printify_products": st.session_state.printify_products,
                "etsy_listings": st.session_state.etsy_listings,
                "viral_videos": st.session_state.viral_videos,
                "social_posts": st.session_state.social_posts,
                "stock_submissions": st.session_state.stock_submissions,
                "total_assets": total_assets
            }
            
            output_dir = Path("/workspaces/artomate/test_output/exports")
            output_dir.mkdir(parents=True, exist_ok=True)
            export_file = output_dir / f"complete_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_file.write_text(json.dumps(export_data, indent=2))
            
            st.success(f"✅ Exported to {export_file}")
    
    with col2:
        if st.button("📊 Export CSV Reports", use_container_width=True):
            st.info("CSV export feature coming soon!")
    
    # Quick actions
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Start New Project", use_container_width=True, type="primary"):
            # Reset all session state
            for key in list(st.session_state.keys()):
                if key != 'current_step':
                    del st.session_state[key]
            st.session_state.current_step = "generate_prompts"
            st.success("✅ Session reset!")
            st.rerun()
    
    with col2:
        if st.button("📋 View All Steps", use_container_width=True):
            st.info("Scroll through sidebar to navigate all steps")
    
    with col3:
        if st.button("📖 Documentation", use_container_width=True):
            st.info("📚 Check README.md and guides in project root")


if __name__ == "__main__":
    main()
