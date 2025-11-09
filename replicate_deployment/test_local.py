#!/usr/bin/env python3
"""Test script for LayoutLMv3 Replicate deployment (local testing)."""

import sys
from PIL import Image
from predict import predict

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_local.py <path_to_receipt_image>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    print(f"Processing receipt: {image_path}")
    
    try:
        image = Image.open(image_path).convert("RGB")
        result = predict(image)
        
        print("\n" + "="*50)
        print("EXTRACTED INFORMATION")
        print("="*50)
        print("\nFormatted Output:")
        print(result['formatted_text'])
        
        print("\n\nEntities:")
        for entity_type, values in result['entities'].items():
            print(f"  {entity_type}: {values}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

