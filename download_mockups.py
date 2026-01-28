#!/usr/bin/env python3
"""Script to download Printify product mockup images."""

import os
import sys
import requests
from pathlib import Path
from loguru import logger

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from artomate.integrations.printify_client import PrintifyClient
from artomate.workers.printify_product_catalog import PRINTIFY_PRODUCTS

def download_mockups():
    """Download mockup images for all products."""
    # Create mockups directory
    mockups_dir = Path(__file__).parent / "data" / "mockups"
    mockups_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📁 Saving mockups to: {mockups_dir}")
    
    # Initialize Printify client
    client = PrintifyClient()
    
    # Track results
    success_count = 0
    failed = []
    
    # Download mockups for each product
    for product_key, product_info in PRINTIFY_PRODUCTS.items():
        blueprint_id = product_info["blueprint_id"]
        logger.info(f"📸 Downloading mockup for {product_key} (blueprint {blueprint_id})...")
        
        try:
            # Get mockup URL from Printify
            mockup_url = client.get_blueprint_mockup_url(blueprint_id)
            
            if mockup_url:
                # Download image
                response = requests.get(mockup_url, timeout=30)
                response.raise_for_status()
                
                # Save image
                image_path = mockups_dir / f"{product_key}.png"
                image_path.write_bytes(response.content)
                
                logger.success(f"✅ Saved: {image_path}")
                success_count += 1
            else:
                logger.warning(f"⚠️  No mockup URL for {product_key}")
                failed.append(product_key)
                
        except Exception as e:
            logger.error(f"❌ Failed to download {product_key}: {e}")
            failed.append(product_key)
    
    # Print summary
    logger.info("=" * 60)
    logger.info(f"📊 Summary:")
    logger.info(f"  ✅ Downloaded: {success_count}")
    logger.info(f"  ❌ Failed: {len(failed)}")
    
    if failed:
        logger.info(f"  Failed products: {', '.join(failed)}")

if __name__ == "__main__":
    download_mockups()
