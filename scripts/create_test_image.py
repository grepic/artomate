"""Create a test image for product crop testing."""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_test_image():
    """Create a colorful test image with a gradient and text."""

    # Create image (3000x3000 for high quality)
    width, height = 3000, 3000
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Draw gradient background
    for y in range(height):
        # Rainbow gradient from top to bottom
        r = int(255 * (y / height))
        g = int(255 * (1 - abs(0.5 - y/height) * 2))
        b = int(255 * (1 - y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Draw colorful circle in center
    center_x, center_y = width // 2, height // 2
    circle_radius = 800
    draw.ellipse(
        [center_x - circle_radius, center_y - circle_radius,
         center_x + circle_radius, center_y + circle_radius],
        fill=(255, 200, 50),
        outline=(50, 50, 50),
        width=20
    )

    # Draw smaller circles for decoration
    for angle in [0, 60, 120, 180, 240, 300]:
        import math
        rad = math.radians(angle)
        x = center_x + int(600 * math.cos(rad))
        y = center_y + int(600 * math.sin(rad))
        draw.ellipse(
            [x - 150, y - 150, x + 150, y + 150],
            fill=(255, 100, 200),
            outline=(255, 255, 255),
            width=10
        )

    # Add text overlays
    try:
        # Try to use a large default font
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 150)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 80)
    except:
        # Fallback to default
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw main text
    text = "TEST IMAGE"
    bbox = draw.textbbox((0, 0), text, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (width - text_width) // 2
    text_y = center_y - 100

    # Draw text with outline
    for offset_x in [-5, 5, 0, 0]:
        for offset_y in [-5, 5, 0, 0] if offset_x == 0 else [0]:
            if offset_x != 0 or offset_y != 0:
                draw.text((text_x + offset_x, text_y + offset_y), text,
                         fill=(0, 0, 0), font=font_large)
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font_large)

    # Draw dimension text
    dim_text = "3000 × 3000"
    bbox = draw.textbbox((0, 0), dim_text, font=font_small)
    dim_width = bbox[2] - bbox[0]
    dim_x = (width - dim_width) // 2
    dim_y = center_y + 150

    for offset_x in [-3, 3, 0, 0]:
        for offset_y in [-3, 3, 0, 0] if offset_x == 0 else [0]:
            if offset_x != 0 or offset_y != 0:
                draw.text((dim_x + offset_x, dim_y + offset_y), dim_text,
                         fill=(0, 0, 0), font=font_small)
    draw.text((dim_x, dim_y), dim_text, fill=(255, 255, 255), font=font_small)

    # Draw corner markers to show orientation
    corner_size = 200
    # Top-left
    draw.rectangle([0, 0, corner_size, corner_size], fill=(255, 0, 0))
    # Top-right
    draw.rectangle([width - corner_size, 0, width, corner_size], fill=(0, 255, 0))
    # Bottom-left
    draw.rectangle([0, height - corner_size, corner_size, height], fill=(0, 0, 255))
    # Bottom-right
    draw.rectangle([width - corner_size, height - corner_size, width, height], fill=(255, 255, 0))

    # Save
    output_path = Path("test_images/test_image.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format='PNG', dpi=(300, 300), optimize=True)

    print(f"✓ Created test image: {output_path}")
    print(f"  Size: {width}x{height} pixels")
    print(f"  File size: {output_path.stat().st_size / 1024:.2f} KB")

    return output_path

if __name__ == "__main__":
    create_test_image()
