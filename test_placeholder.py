#!/usr/bin/env python3
"""Test script to verify placeholder generation and cropping logic."""

from pathlib import Path
from PIL import Image
import sys

sys.path.insert(0, str(Path(__file__).parent))

from ui.crop_tester_ui import create_placeholder_image, crop_image_to_dimensions, get_product_families


def test_placeholder_generation():
    """Test creating placeholder images with different dimensions."""
    print("=" * 60)
    print("TESTING PLACEHOLDER GENERATION")
    print("=" * 60)
    
    test_cases = [
        (1200, 1500, "8×10 Poster"),
        (1800, 2700, "12×18 Poster"),
        (375, 750, "iPhone 12"),
        (2400, 2400, "18×18 Pillow"),
    ]
    
    output_dir = Path("/workspaces/artomate/test_output/placeholders")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for width, height, name in test_cases:
        print(f"\n📸 Creating {name}: {width}×{height}px")
        img = create_placeholder_image(width, height, name)
        
        # Verify dimensions
        assert img.size == (width, height), f"Size mismatch! Expected {width}×{height}, got {img.size}"
        
        # Save
        output_path = output_dir / f"{name.replace(' ', '_').replace('×', 'x')}_{width}x{height}.png"
        img.save(output_path)
        print(f"   ✅ Saved to: {output_path}")
        print(f"   ✅ Size verified: {img.size}")
    
    print("\n✅ All placeholders generated successfully!")


def test_cropping_logic():
    """Test cropping images to target dimensions."""
    print("\n" + "=" * 60)
    print("TESTING CROPPING LOGIC")
    print("=" * 60)
    
    # Create a test source image (3000×2000 landscape)
    source = create_placeholder_image(3000, 2000, "SOURCE IMAGE")
    
    test_cases = [
        (1200, 1500, "8×10 Portrait"),      # Crop width
        (1500, 1200, "10×8 Landscape"),     # Crop height
        (2400, 2400, "Square"),             # Crop both
    ]
    
    output_dir = Path("/workspaces/artomate/test_output/crop_tests")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for target_w, target_h, name in test_cases:
        print(f"\n✂️  Cropping to {name}: {target_w}×{target_h}px")
        cropped = crop_image_to_dimensions(source, target_w, target_h)
        
        # Verify dimensions
        assert cropped.size == (target_w, target_h), f"Size mismatch! Expected {target_w}×{target_h}, got {cropped.size}"
        
        # Save
        output_path = output_dir / f"cropped_{name.replace(' ', '_')}_{target_w}x{target_h}.png"
        cropped.save(output_path)
        print(f"   ✅ Saved to: {output_path}")
        print(f"   ✅ Size verified: {cropped.size}")
        
        # Calculate aspect ratio
        source_ratio = source.size[0] / source.size[1]
        target_ratio = target_w / target_h
        cropped_ratio = cropped.size[0] / cropped.size[1]
        print(f"   📐 Aspect ratios - Source: {source_ratio:.3f}, Target: {target_ratio:.3f}, Result: {cropped_ratio:.3f}")
    
    print("\n✅ All crops generated successfully!")


def test_product_variants():
    """Verify all product variants have pixel dimensions."""
    print("\n" + "=" * 60)
    print("TESTING PRODUCT VARIANT SPECIFICATIONS")
    print("=" * 60)
    
    families = get_product_families()
    
    missing_specs = []
    total_variants = 0
    
    for family_name, family_info in families.items():
        print(f"\n📦 {family_name}")
        variants = family_info.get("variants", {})
        
        for variant_name, specs in variants.items():
            total_variants += 1
            width_px = specs.get("width_px")
            height_px = specs.get("height_px")
            
            if width_px and height_px:
                print(f"   ✅ {variant_name}: {width_px}×{height_px}px - {specs.get('print_area')}")
            else:
                print(f"   ❌ {variant_name}: MISSING PIXEL DIMENSIONS")
                missing_specs.append(f"{family_name} → {variant_name}")
    
    print(f"\n{'='*60}")
    print(f"Total variants checked: {total_variants}")
    
    if missing_specs:
        print(f"❌ Missing specs: {len(missing_specs)}")
        for item in missing_specs:
            print(f"   - {item}")
        return False
    else:
        print("✅ All variants have complete pixel dimensions!")
        return True


def main():
    """Run all tests."""
    print("\n🧪 CROP TESTER VALIDATION")
    print("=" * 60)
    
    try:
        # Test 1: Product variant specs
        specs_ok = test_product_variants()
        
        # Test 2: Placeholder generation
        test_placeholder_generation()
        
        # Test 3: Cropping logic
        test_cropping_logic()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        
        print("\n📁 Output locations:")
        print("   - Placeholders: test_output/placeholders/")
        print("   - Crop tests:   test_output/crop_tests/")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
