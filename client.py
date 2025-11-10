"""Minimal client to chain DeepSeekOCR and LayoutLMv3 Replicate models."""

import os
import replicate
from PIL import Image
from typing import Dict, List, Tuple
import re


def extract_words_and_boxes(text: str, image_width: int, image_height: int) -> Tuple[List[str], List[List[int]]]:
    """
    Extract words from OCR text and estimate bounding boxes.
    
    This is a simple estimation - for better accuracy, use an OCR that provides boxes.
    
    Args:
        text: OCR text output
        image_width: Image width in pixels
        image_height: Image height in pixels
        
    Returns:
        Tuple of (words list, boxes list)
    """
    # Split text into words
    words = re.findall(r'\S+', text)
    
    if not words:
        return [], []
    
    # Simple estimation: distribute words evenly across image
    # This is a placeholder - for production, use OCR that provides actual boxes
    boxes = []
    words_per_line = max(1, int(len(words) ** 0.5))  # Rough estimate
    num_lines = (len(words) + words_per_line - 1) // words_per_line
    
    line_height = image_height // max(num_lines, 1)
    char_width = image_width // max(max(len(w) for w in words), 1)
    
    for i, word in enumerate(words):
        line = i // words_per_line
        pos_in_line = i % words_per_line
        
        # Estimate box position
        x0 = pos_in_line * char_width * (len(word) + 1)
        y0 = line * line_height
        x1 = x0 + len(word) * char_width
        y1 = y0 + line_height
        
        # Ensure boxes are within image bounds
        x0 = max(0, min(x0, image_width - 1))
        y0 = max(0, min(y0, image_height - 1))
        x1 = max(x0 + 1, min(x1, image_width))
        y1 = max(y0 + 1, min(y1, image_height))
        
        boxes.append([int(x0), int(y0), int(x1), int(y1)])
    
    return words, boxes


def process_receipt(
    image_path: str,
    deepseekocr_model: str = "YOUR_USERNAME/deepseekocr",
    layoutlmv3_model: str = "YOUR_USERNAME/layoutlmv3-receipts"
) -> Dict:
    """
    Process receipt image through DeepSeekOCR and LayoutLMv3 pipeline.
    
    Args:
        image_path: Path to receipt image file
        deepseekocr_model: Replicate model name for DeepSeekOCR
        layoutlmv3_model: Replicate model name for LayoutLMv3
        
    Returns:
        Dictionary with structured receipt entities
    """
    # Check API token
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        raise ValueError("REPLICATE_API_TOKEN environment variable not set")
    
    client = replicate.Client(api_token=api_token)
    
    # Step 1: Run DeepSeekOCR
    print("Running DeepSeekOCR...")
    with open(image_path, "rb") as f:
        ocr_output = client.run(
            deepseekocr_model,
            input={"image": f}
        )
    
    # Handle different output formats
    if isinstance(ocr_output, dict):
        ocr_text = ocr_output.get("text", "")
    elif isinstance(ocr_output, str):
        ocr_text = ocr_output
    else:
        ocr_text = str(ocr_output)
    
    if not ocr_text:
        return {
            "entities": {},
            "formatted_text": "No text extracted from image.",
            "error": "OCR returned empty result"
        }
    
    print(f"OCR extracted text: {ocr_text[:100]}...")
    
    # Step 2: Extract words and estimate boxes
    img = Image.open(image_path)
    words, boxes = extract_words_and_boxes(ocr_text, img.width, img.height)
    
    if not words:
        return {
            "entities": {},
            "formatted_text": "No text detected in image.",
            "error": "No words extracted from OCR"
        }
    
    print(f"Extracted {len(words)} words")
    
    # Step 3: Run LayoutLMv3
    print("Running LayoutLMv3...")
    with open(image_path, "rb") as f:
        result = client.run(
            layoutlmv3_model,
            input={
                "image": f,
                "words": words,
                "boxes": boxes
            }
        )
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python client.py <image_path>")
        print("Set REPLICATE_API_TOKEN environment variable")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Update these with your actual Replicate model names
    DEEPSEEKOCR_MODEL = "whidge/deepseekocr"
    LAYOUTLMV3_MODEL = "whidge/layoutlmv3"
    
    try:
        result = process_receipt(image_path, DEEPSEEKOCR_MODEL, LAYOUTLMV3_MODEL)
        print("\n=== Results ===")
        print(result.get("formatted_text", result))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
