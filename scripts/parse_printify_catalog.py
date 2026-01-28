"""Parse Printify XML catalog and extract all products, variants, and print areas."""

import sys
from pathlib import Path
from typing import Dict, List, Set
import xml.etree.ElementTree as ET
from collections import defaultdict
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger


def parse_catalog(xml_path: Path) -> Dict:
    """Parse Printify XML catalog.
    
    Args:
        xml_path: Path to XML catalog
        
    Returns:
        Dict with parsed data
    """
    logger.info(f"Parsing XML catalog: {xml_path}")
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    blueprints = []
    unique_sizes = set()
    unique_colors = set()
    unique_positions = set()
    
    for blueprint in root.findall('blueprint'):
        blueprint_id = blueprint.get('id')
        blueprint_title = blueprint.get('title')
        blueprint_brand = blueprint.get('brand', '')
        blueprint_model = blueprint.get('model', '')
        
        logger.info(f"Processing blueprint {blueprint_id}: {blueprint_title}")
        
        providers = []
        
        for provider in blueprint.findall('print_provider'):
            provider_id = provider.get('id')
            provider_title = provider.get('title')
            
            variants = []
            print_areas = defaultdict(set)  # position -> set of (width, height)
            
            for variant in provider.findall('variant'):
                variant_id = variant.get('id')
                variant_title = variant.get('title')
                
                # Extract options
                options = {}
                for option in variant.findall('option'):
                    name = option.get('name')
                    value = option.get('value')
                    options[name] = value
                    
                    if name == 'size':
                        unique_sizes.add(value)
                    elif name == 'color':
                        unique_colors.add(value)
                
                # Extract placeholders (print areas)
                placeholders = []
                for placeholder in variant.findall('placeholder'):
                    position = placeholder.get('position')
                    width = int(placeholder.get('width'))
                    height = int(placeholder.get('height'))
                    
                    placeholders.append({
                        'position': position,
                        'width': width,
                        'height': height,
                    })
                    
                    unique_positions.add(position)
                    print_areas[position].add((width, height))
                
                variants.append({
                    'id': variant_id,
                    'title': variant_title,
                    'options': options,
                    'placeholders': placeholders,
                })
            
            # Convert sets to lists for JSON serialization
            print_areas_list = {}
            for pos, dimensions in print_areas.items():
                print_areas_list[pos] = [
                    {'width': w, 'height': h} for w, h in sorted(dimensions)
                ]
            
            providers.append({
                'id': provider_id,
                'title': provider_title,
                'variant_count': len(variants),
                'print_areas': print_areas_list,
                'variants': variants[:5],  # Only include first 5 variants as sample
            })
        
        blueprints.append({
            'id': blueprint_id,
            'title': blueprint_title,
            'brand': blueprint_brand,
            'model': blueprint_model,
            'provider_count': len(providers),
            'providers': providers,
        })
    
    result = {
        'total_blueprints': len(blueprints),
        'unique_sizes': sorted(list(unique_sizes)),
        'unique_colors': sorted(list(unique_colors)),
        'unique_positions': sorted(list(unique_positions)),
        'blueprints': blueprints,
    }
    
    logger.info(f"Parsed {len(blueprints)} blueprints")
    logger.info(f"Found {len(unique_sizes)} unique sizes")
    logger.info(f"Found {len(unique_colors)} unique colors")
    logger.info(f"Found {len(unique_positions)} unique print positions")
    
    return result


def create_summary(data: Dict) -> str:
    """Create human-readable summary.
    
    Args:
        data: Parsed catalog data
        
    Returns:
        Summary text
    """
    lines = []
    lines.append("=" * 80)
    lines.append("PRINTIFY CATALOG SUMMARY")
    lines.append("=" * 80)
    lines.append(f"\nTotal Blueprints: {data['total_blueprints']}")
    lines.append(f"Unique Sizes: {len(data['unique_sizes'])}")
    lines.append(f"Unique Colors: {len(data['unique_colors'])}")
    lines.append(f"Unique Print Positions: {len(data['unique_positions'])}")
    
    lines.append(f"\nPrint Positions: {', '.join(data['unique_positions'])}")
    
    lines.append("\n" + "=" * 80)
    lines.append("BLUEPRINTS BY CATEGORY")
    lines.append("=" * 80)
    
    # Group by category (based on title keywords)
    categories = defaultdict(list)
    
    for bp in data['blueprints']:
        title = bp['title'].lower()
        
        if any(kw in title for kw in ['tee', 't-shirt', 'tank', 'shirt']):
            category = 'Apparel - Shirts'
        elif any(kw in title for kw in ['hoodie', 'sweatshirt', 'jacket']):
            category = 'Apparel - Outerwear'
        elif any(kw in title for kw in ['poster', 'print', 'canvas']):
            category = 'Wall Art'
        elif any(kw in title for kw in ['mug', 'cup', 'tumbler', 'bottle']):
            category = 'Drinkware'
        elif any(kw in title for kw in ['pillow', 'blanket', 'towel', 'rug']):
            category = 'Home & Living'
        elif any(kw in title for kw in ['phone', 'case', 'bag', 'tote']):
            category = 'Accessories'
        else:
            category = 'Other'
        
        categories[category].append(bp)
    
    for category in sorted(categories.keys()):
        items = categories[category]
        lines.append(f"\n{category} ({len(items)} items):")
        for item in items[:10]:  # Show first 10
            lines.append(f"  • [{item['id']}] {item['title']} ({item['provider_count']} providers)")
        if len(items) > 10:
            lines.append(f"  ... and {len(items) - 10} more")
    
    return "\n".join(lines)


def main():
    """Main entry point."""
    xml_path = Path(__file__).parent.parent / "data" / "printify_catalog_full.xml"
    
    if not xml_path.exists():
        logger.error(f"XML file not found: {xml_path}")
        sys.exit(1)
    
    # Parse catalog
    data = parse_catalog(xml_path)
    
    # Save full data as JSON
    output_json = Path(__file__).parent.parent / "data" / "printify_catalog_parsed.json"
    with open(output_json, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved full data to: {output_json}")
    
    # Create and save summary
    summary = create_summary(data)
    print("\n" + summary)
    
    output_summary = Path(__file__).parent.parent / "data" / "printify_catalog_summary.txt"
    with open(output_summary, 'w') as f:
        f.write(summary)
    logger.info(f"Saved summary to: {output_summary}")
    
    # Create simplified product list
    products_simple = []
    for bp in data['blueprints']:
        for provider in bp['providers']:
            print_areas = []
            for pos, dims in provider['print_areas'].items():
                for dim in dims:
                    print_areas.append({
                        'position': pos,
                        'width': dim['width'],
                        'height': dim['height'],
                    })
            
            products_simple.append({
                'blueprint_id': bp['id'],
                'title': bp['title'],
                'brand': bp['brand'],
                'provider_id': provider['id'],
                'provider': provider['title'],
                'variant_count': provider['variant_count'],
                'print_areas': print_areas,
            })
    
    output_simple = Path(__file__).parent.parent / "data" / "printify_products_simple.json"
    with open(output_simple, 'w') as f:
        json.dump(products_simple, f, indent=2)
    logger.info(f"Saved simplified product list to: {output_simple}")
    
    logger.info("\n✅ Done!")


if __name__ == "__main__":
    main()
