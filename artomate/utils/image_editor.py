"""Image editor with crop, resize, filters, and watermark."""

import logging
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

logger = logging.getLogger(__name__)


class FilterType(str, Enum):
    """Available image filters."""

    NONE = "none"
    BLUR = "blur"
    SHARPEN = "sharpen"
    CONTOUR = "contour"
    DETAIL = "detail"
    EDGE_ENHANCE = "edge_enhance"
    SMOOTH = "smooth"
    GRAYSCALE = "grayscale"
    SEPIA = "sepia"
    VINTAGE = "vintage"


class WatermarkPosition(str, Enum):
    """Watermark positioning."""

    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"


class ImageEditor:
    """Image editing operations."""

    def __init__(self, image_path: Path):
        """Initialize editor with an image."""
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.original_image = self.image.copy()
        logger.info(f"Loaded image: {image_path} ({self.image.size})")

    def reset(self):
        """Reset to original image."""
        self.image = self.original_image.copy()

    def crop(
        self, x: int, y: int, width: int, height: int, smart_crop: bool = False
    ) -> "ImageEditor":
        """Crop image to specified dimensions."""
        if smart_crop:
            # Smart crop tries to center on interesting content
            self.image = self._smart_crop(width, height)
        else:
            # Manual crop
            self.image = self.image.crop((x, y, x + width, y + height))

        logger.info(f"Cropped to {self.image.size}")
        return self

    def _smart_crop(self, target_width: int, target_height: int) -> Image.Image:
        """Smart crop focusing on content."""
        img_width, img_height = self.image.size
        target_ratio = target_width / target_height
        img_ratio = img_width / img_height

        if img_ratio > target_ratio:
            # Image is wider - crop horizontally
            new_width = int(img_height * target_ratio)
            left = (img_width - new_width) // 2
            return self.image.crop((left, 0, left + new_width, img_height))
        else:
            # Image is taller - crop vertically
            new_height = int(img_width / target_ratio)
            top = (img_height - new_height) // 2
            return self.image.crop((0, top, img_width, top + new_height))

    def resize(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_aspect: bool = True,
        quality: str = "high",
    ) -> "ImageEditor":
        """Resize image."""
        if not width and not height:
            raise ValueError("Must specify width or height")

        img_width, img_height = self.image.size

        if maintain_aspect:
            if width and not height:
                ratio = width / img_width
                height = int(img_height * ratio)
            elif height and not width:
                ratio = height / img_height
                width = int(img_width * ratio)

        # Choose resampling method
        resample = {
            "high": Image.Resampling.LANCZOS,
            "medium": Image.Resampling.BILINEAR,
            "fast": Image.Resampling.NEAREST,
        }.get(quality, Image.Resampling.LANCZOS)

        self.image = self.image.resize((width, height), resample)
        logger.info(f"Resized to {self.image.size}")
        return self

    def apply_filter(self, filter_type: FilterType, intensity: float = 1.0) -> "ImageEditor":
        """Apply image filter."""
        if filter_type == FilterType.NONE:
            return self

        # PIL filters
        if filter_type == FilterType.BLUR:
            self.image = self.image.filter(ImageFilter.GaussianBlur(radius=2 * intensity))
        elif filter_type == FilterType.SHARPEN:
            self.image = self.image.filter(ImageFilter.SHARPEN)
        elif filter_type == FilterType.CONTOUR:
            self.image = self.image.filter(ImageFilter.CONTOUR)
        elif filter_type == FilterType.DETAIL:
            self.image = self.image.filter(ImageFilter.DETAIL)
        elif filter_type == FilterType.EDGE_ENHANCE:
            self.image = self.image.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_type == FilterType.SMOOTH:
            self.image = self.image.filter(ImageFilter.SMOOTH)

        # Custom filters
        elif filter_type == FilterType.GRAYSCALE:
            self.image = self.image.convert("L").convert("RGB")

        elif filter_type == FilterType.SEPIA:
            self.image = self._apply_sepia()

        elif filter_type == FilterType.VINTAGE:
            self.image = self._apply_vintage()

        logger.info(f"Applied filter: {filter_type}")
        return self

    def _apply_sepia(self) -> Image.Image:
        """Apply sepia tone effect."""
        img = self.image.convert("RGB")
        pixels = img.load()
        width, height = img.size

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]

                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)

                pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))

        return img

    def _apply_vintage(self) -> Image.Image:
        """Apply vintage effect."""
        # Reduce contrast
        img = self.image
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(0.8)

        # Add slight sepia
        img = img.convert("RGB")
        r, g, b = img.split()
        r = r.point(lambda i: i * 1.1)
        g = g.point(lambda i: i * 1.05)
        b = b.point(lambda i: i * 0.9)
        img = Image.merge("RGB", (r, g, b))

        # Reduce saturation
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.7)

        return img

    def adjust_brightness(self, factor: float) -> "ImageEditor":
        """Adjust brightness (1.0 = no change, >1.0 brighter, <1.0 darker)."""
        enhancer = ImageEnhance.Brightness(self.image)
        self.image = enhancer.enhance(factor)
        logger.info(f"Adjusted brightness: {factor}")
        return self

    def adjust_contrast(self, factor: float) -> "ImageEditor":
        """Adjust contrast (1.0 = no change)."""
        enhancer = ImageEnhance.Contrast(self.image)
        self.image = enhancer.enhance(factor)
        logger.info(f"Adjusted contrast: {factor}")
        return self

    def adjust_saturation(self, factor: float) -> "ImageEditor":
        """Adjust color saturation (1.0 = no change, 0.0 = grayscale)."""
        enhancer = ImageEnhance.Color(self.image)
        self.image = enhancer.enhance(factor)
        logger.info(f"Adjusted saturation: {factor}")
        return self

    def add_text(
        self,
        text: str,
        position: Tuple[int, int],
        font_size: int = 40,
        color: Tuple[int, int, int] = (255, 255, 255),
        font_path: Optional[Path] = None,
        outline_color: Optional[Tuple[int, int, int]] = None,
        outline_width: int = 2,
    ) -> "ImageEditor":
        """Add text overlay to image."""
        draw = ImageDraw.Draw(self.image)

        try:
            if font_path and font_path.exists():
                font = ImageFont.truetype(str(font_path), font_size)
            else:
                font = ImageFont.load_default()
        except Exception as e:
            logger.warning(f"Failed to load font: {e}, using default")
            font = ImageFont.load_default()

        # Draw outline if specified
        if outline_color:
            for adj_x in range(-outline_width, outline_width + 1):
                for adj_y in range(-outline_width, outline_width + 1):
                    draw.text(
                        (position[0] + adj_x, position[1] + adj_y), text, font=font, fill=outline_color
                    )

        # Draw main text
        draw.text(position, text, font=font, fill=color)
        logger.info(f"Added text: '{text}' at {position}")
        return self

    def add_watermark(
        self,
        watermark_text: str,
        position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT,
        opacity: float = 0.5,
        font_size: int = 30,
        padding: int = 20,
    ) -> "ImageEditor":
        """Add watermark to image."""
        # Create watermark layer
        watermark = Image.new("RGBA", self.image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark)

        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

        # Calculate text size
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position
        if position == WatermarkPosition.TOP_LEFT:
            pos = (padding, padding)
        elif position == WatermarkPosition.TOP_RIGHT:
            pos = (self.image.width - text_width - padding, padding)
        elif position == WatermarkPosition.BOTTOM_LEFT:
            pos = (padding, self.image.height - text_height - padding)
        elif position == WatermarkPosition.BOTTOM_RIGHT:
            pos = (
                self.image.width - text_width - padding,
                self.image.height - text_height - padding,
            )
        else:  # CENTER
            pos = (
                (self.image.width - text_width) // 2,
                (self.image.height - text_height) // 2,
            )

        # Draw watermark
        alpha = int(255 * opacity)
        draw.text(pos, watermark_text, fill=(255, 255, 255, alpha), font=font)

        # Composite
        if self.image.mode != "RGBA":
            self.image = self.image.convert("RGBA")

        self.image = Image.alpha_composite(self.image, watermark)
        logger.info(f"Added watermark: '{watermark_text}' at {position}")
        return self

    def rotate(self, degrees: float, expand: bool = True) -> "ImageEditor":
        """Rotate image."""
        self.image = self.image.rotate(degrees, expand=expand, fillcolor="white")
        logger.info(f"Rotated {degrees} degrees")
        return self

    def flip_horizontal(self) -> "ImageEditor":
        """Flip image horizontally."""
        self.image = self.image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        logger.info("Flipped horizontally")
        return self

    def flip_vertical(self) -> "ImageEditor":
        """Flip image vertically."""
        self.image = self.image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        logger.info("Flipped vertically")
        return self

    def save(
        self,
        output_path: Path,
        format: Optional[str] = None,
        quality: int = 95,
        optimize: bool = True,
    ) -> Path:
        """Save edited image."""
        # Convert RGBA to RGB if saving as JPEG
        if format == "JPEG" or (not format and output_path.suffix.lower() in [".jpg", ".jpeg"]):
            if self.image.mode == "RGBA":
                rgb_image = Image.new("RGB", self.image.size, (255, 255, 255))
                rgb_image.paste(self.image, mask=self.image.split()[3])
                self.image = rgb_image

        self.image.save(output_path, format=format, quality=quality, optimize=optimize)
        logger.info(f"Saved edited image to {output_path}")
        return output_path

    def get_image(self) -> Image.Image:
        """Get current PIL Image object."""
        return self.image

    def get_thumbnail(self, max_size: Tuple[int, int] = (200, 200)) -> Image.Image:
        """Get thumbnail version of current image."""
        thumbnail = self.image.copy()
        thumbnail.thumbnail(max_size, Image.Resampling.LANCZOS)
        return thumbnail
