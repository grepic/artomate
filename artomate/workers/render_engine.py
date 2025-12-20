"""Image rendering and cropping engine using Pillow."""

from datetime import datetime
from pathlib import Path
from typing import Literal, Optional, Tuple

from loguru import logger
from PIL import Image, ImageOps

from artomate.core.config import Config, get_config
from artomate.db.database import get_db
from artomate.db.models import Asset, PrintFile


CropMode = Literal["contain", "cover", "smart_crop"]


class RenderEngine:
    """Handles image cropping, resizing, and print file preparation."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize render engine.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        self.db = get_db()

    def calculate_dimensions(
        self,
        source_width: int,
        source_height: int,
        target_width: int,
        target_height: int,
        mode: CropMode = "cover",
    ) -> Tuple[int, int, int, int]:
        """Calculate crop/resize dimensions.

        Args:
            source_width: Source image width
            source_height: Source image height
            target_width: Target width
            target_height: Target height
            mode: Crop mode

        Returns:
            Tuple of (new_width, new_height, crop_x, crop_y)
        """
        source_ratio = source_width / source_height
        target_ratio = target_width / target_height

        if mode == "contain":
            # Fit entire image, may have borders
            if source_ratio > target_ratio:
                # Source is wider
                new_width = target_width
                new_height = int(target_width / source_ratio)
            else:
                # Source is taller
                new_height = target_height
                new_width = int(target_height * source_ratio)

            return new_width, new_height, 0, 0

        elif mode == "cover":
            # Fill entire target area, may crop
            if source_ratio > target_ratio:
                # Source is wider - fit height
                new_height = target_height
                new_width = int(target_height * source_ratio)
            else:
                # Source is taller - fit width
                new_width = target_width
                new_height = int(target_width / source_ratio)

            # Center crop
            crop_x = (new_width - target_width) // 2
            crop_y = (new_height - target_height) // 2

            return new_width, new_height, crop_x, crop_y

        elif mode == "smart_crop":
            # Smart crop (for MVP, same as cover; can add ML-based cropping later)
            return self.calculate_dimensions(
                source_width, source_height, target_width, target_height, mode="cover"
            )

        else:
            raise ValueError(f"Unknown crop mode: {mode}")

    def render_image(
        self,
        source_path: Path | str,
        target_width: int,
        target_height: int,
        mode: CropMode = "cover",
        dpi: int = 300,
        background_color: str = "white",
        transparent_background: bool = False,
        remove_white_bg: bool = False,
    ) -> Image.Image:
        """Render image to target dimensions.

        Args:
            source_path: Path to source image
            target_width: Target width in pixels
            target_height: Target height in pixels
            mode: Crop mode
            dpi: DPI for print
            background_color: Background color for contain mode (if not transparent)
            transparent_background: Create PNG with transparent background
            remove_white_bg: Remove white background from source (for AI images)

        Returns:
            Rendered PIL Image

        Raises:
            FileNotFoundError: If source image not found
            ValueError: If rendering fails
        """
        source_path = Path(source_path)

        if not source_path.exists():
            raise FileNotFoundError(f"Source image not found: {source_path}")

        try:
            # Open source image
            with Image.open(source_path) as img:
                # Convert to RGBA if transparent needed, otherwise RGB
                if transparent_background:
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")
                else:
                    if img.mode not in ("RGB", "RGBA"):
                        img = img.convert("RGB")

                # Remove white background if requested (for AI-generated images)
                if remove_white_bg and transparent_background:
                    img = self._remove_white_background(img)

                source_width, source_height = img.size

                logger.debug(
                    f"Rendering {source_width}x{source_height} → {target_width}x{target_height} "
                    f"({mode}, transparent={transparent_background})"
                )

                # Calculate dimensions
                new_width, new_height, crop_x, crop_y = self.calculate_dimensions(
                    source_width, source_height, target_width, target_height, mode
                )

                # Resize
                resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Create target canvas
                if mode == "contain":
                    # Create canvas with background color or transparent
                    if transparent_background:
                        canvas = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
                    else:
                        canvas = Image.new("RGB", (target_width, target_height), background_color)

                    # Paste resized image centered
                    paste_x = (target_width - new_width) // 2
                    paste_y = (target_height - new_height) // 2

                    if transparent_background and resized.mode == "RGBA":
                        canvas.paste(resized, (paste_x, paste_y), resized)
                    else:
                        canvas.paste(resized, (paste_x, paste_y))

                    result = canvas

                else:  # cover or smart_crop
                    # Crop to target size
                    result = resized.crop(
                        (
                            crop_x,
                            crop_y,
                            crop_x + target_width,
                            crop_y + target_height,
                        )
                    )

                # Set DPI
                result.info["dpi"] = (dpi, dpi)

                logger.debug(f"✓ Rendered image: {target_width}x{target_height}")

                return result

        except Exception as e:
            logger.error(f"Failed to render image: {e}")
            raise ValueError(f"Image rendering failed: {e}")

    def _remove_white_background(self, img: Image.Image) -> Image.Image:
        """Remove white background from image and make transparent.

        Args:
            img: PIL Image (RGBA)

        Returns:
            Image with transparent background

        Note:
            Useful for AI-generated images that often have white backgrounds
        """
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Get pixel data
        data = img.getdata()

        new_data = []
        for item in data:
            # Check if pixel is close to white
            # Threshold: RGB values all above 240
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                # Make transparent (alpha = 0)
                new_data.append((255, 255, 255, 0))
            else:
                # Keep original
                new_data.append(item)

        img.putdata(new_data)
        return img

    def create_print_file(
        self,
        asset: Asset,
        target_width: int,
        target_height: int,
        crop_mode: CropMode = "cover",
        dpi: int = 300,
        printify_blueprint_id: Optional[int] = None,
        printify_provider_id: Optional[int] = None,
        transparent_background: bool = False,
        remove_white_bg: bool = False,
    ) -> PrintFile:
        """Create a print-ready file from an asset.

        Args:
            asset: Source asset
            target_width: Target width in pixels
            target_height: Target height in pixels
            crop_mode: Crop mode
            dpi: DPI for print
            printify_blueprint_id: Printify blueprint ID
            printify_provider_id: Printify provider ID
            transparent_background: Create PNG with transparent background (for apparel)
            remove_white_bg: Remove white background from AI-generated images

        Returns:
            Created PrintFile instance

        Raises:
            FileNotFoundError: If source asset not found
            ValueError: If rendering fails
        """
        # Render image
        rendered = self.render_image(
            source_path=asset.storage_path,
            target_width=target_width,
            target_height=target_height,
            mode=crop_mode,
            dpi=dpi,
            transparent_background=transparent_background,
            remove_white_bg=remove_white_bg,
        )

        # Create filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        suffix = "_transparent" if transparent_background else ""
        filename = f"printfile_{asset.job_id}_{timestamp}_{target_width}x{target_height}{suffix}.png"
        save_path = self.config.assets_dir / "printfiles" / filename

        # Ensure directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Save
        rendered.save(save_path, format="PNG", dpi=(dpi, dpi), optimize=True)

        file_size = save_path.stat().st_size

        logger.info(f"✓ Saved print file: {save_path} ({file_size:,} bytes)")

        # Determine color mode
        color_mode = "RGBA" if transparent_background else "RGB"

        # Create PrintFile record
        print_file = PrintFile(
            asset_id=asset.id,
            job_id=asset.job_id,
            target_width=target_width,
            target_height=target_height,
            dpi=dpi,
            color_mode=color_mode,
            crop_mode=crop_mode,
            storage_path=str(save_path),
            file_size_bytes=file_size,
            printify_blueprint_id=printify_blueprint_id,
            printify_print_provider_id=printify_provider_id,
            print_area_data={
                "source_asset_id": asset.id,
                "rendered_at": datetime.utcnow().isoformat(),
                "transparent_background": transparent_background,
                "remove_white_bg": remove_white_bg,
            },
        )

        # Save to database
        with self.db.session_scope() as session:
            session.add(print_file)
            session.flush()

            logger.info(f"✓ Created print file record {print_file.id}")

        return print_file

    def create_print_files_for_blueprints(
        self,
        asset: Asset,
        blueprint_specs: list[dict],
        crop_mode: CropMode = "cover",
    ) -> list[PrintFile]:
        """Create multiple print files for different blueprints.

        Args:
            asset: Source asset
            blueprint_specs: List of blueprint specifications
                Each dict should have: {
                    "blueprint_id": int,
                    "provider_id": int,
                    "width": int,
                    "height": int,
                }
            crop_mode: Crop mode

        Returns:
            List of created PrintFile instances
        """
        print_files = []

        for spec in blueprint_specs:
            try:
                print_file = self.create_print_file(
                    asset=asset,
                    target_width=spec["width"],
                    target_height=spec["height"],
                    crop_mode=crop_mode,
                    printify_blueprint_id=spec.get("blueprint_id"),
                    printify_provider_id=spec.get("provider_id"),
                )

                print_files.append(print_file)

            except Exception as e:
                logger.error(
                    f"Failed to create print file for blueprint {spec.get('blueprint_id')}: {e}"
                )
                continue

        logger.info(f"✓ Created {len(print_files)} print file(s) for asset {asset.id}")

        return print_files

    def optimize_for_web(
        self,
        source_path: Path | str,
        output_path: Path | str,
        max_width: int = 1200,
        quality: int = 85,
    ) -> dict:
        """Optimize image for web display (e.g., mockups, gallery).

        Args:
            source_path: Source image path
            output_path: Output path
            max_width: Maximum width
            quality: JPEG quality (1-100)

        Returns:
            Dict with optimized image info

        Raises:
            FileNotFoundError: If source not found
        """
        source_path = Path(source_path)
        output_path = Path(output_path)

        if not source_path.exists():
            raise FileNotFoundError(f"Source image not found: {source_path}")

        with Image.open(source_path) as img:
            # Convert to RGB
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Resize if needed
            width, height = img.size
            if width > max_width:
                ratio = max_width / width
                new_height = int(height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # Save optimized
            output_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path, format="JPEG", quality=quality, optimize=True)

            file_size = output_path.stat().st_size

            logger.info(f"✓ Optimized for web: {output_path} ({file_size:,} bytes)")

            return {
                "path": str(output_path),
                "width": img.size[0],
                "height": img.size[1],
                "size_bytes": file_size,
            }

    def create_mockup(
        self,
        asset: Asset,
        mockup_template: str = "simple",
    ) -> Optional[Asset]:
        """Create product mockup (placeholder for MVP).

        Args:
            asset: Source asset
            mockup_template: Mockup template type

        Returns:
            Mockup Asset instance or None

        Note:
            For MVP, this is a placeholder. Can be enhanced with:
            - Printify mockup API
            - Custom mockup templates
            - Third-party mockup services
        """
        logger.info(f"Mockup generation not yet implemented (asset {asset.id})")
        return None
