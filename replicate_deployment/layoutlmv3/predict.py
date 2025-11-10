"""Replicate prediction script for LayoutLMv3 CORD receipt processing with external OCR."""

import torch
from PIL import Image
from typing import Dict, List
from transformers import (
    AutoModelForTokenClassification,
    LayoutLMv3ImageProcessor,
    RobertaTokenizer
)
from cog import BasePredictor, Input, Path

MODEL_NAME = "nielsr/layoutlmv3-finetuned-cord"
BASE_MODEL = "microsoft/layoutlmv3-base"


class Predictor(BasePredictor):
    """Cog Predictor class for LayoutLMv3 receipt processing."""
    
    def setup(self):
        """Load model components once at startup."""
        print("Loading LayoutLMv3 model components...")
        self.image_processor = LayoutLMv3ImageProcessor.from_pretrained(BASE_MODEL)
        self.tokenizer = RobertaTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)
        
        # Move to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.model.eval()
        print(f"Model loaded on {self.device}")

    def process_receipt(self, image: Image.Image, words: List[str], boxes: List[List[int]]) -> Dict:
        """Process receipt image with OCR results and extract structured information."""
        
        if not words or not boxes:
            return {
                "entities": {},
                "formatted_text": "No text provided.",
                "tokens": [],
                "predictions": []
            }
        
        # Ensure words and boxes have same length
        if len(words) != len(boxes):
            return {
                "entities": {},
                "formatted_text": f"Error: words ({len(words)}) and boxes ({len(boxes)}) count mismatch.",
                "tokens": [],
                "predictions": []
            }
        
        # Tokenize text with bounding boxes
        encoded_inputs = self.tokenizer(
            words,
            boxes=boxes,
            padding="max_length",
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Process image
        image_inputs = self.image_processor(image, return_tensors="pt")
        
        # Move to device
        encoded_inputs = {k: v.to(self.device) for k, v in encoded_inputs.items()}
        image_inputs = {k: v.to(self.device) for k, v in image_inputs.items()}
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(
                input_ids=encoded_inputs["input_ids"],
                bbox=encoded_inputs["bbox"],
                attention_mask=encoded_inputs["attention_mask"],
                pixel_values=image_inputs["pixel_values"]
            )
        
        # Get predictions
        predictions = torch.argmax(outputs.logits, dim=-1)[0].cpu().numpy()
        
        # Get label names
        id2label = self.model.config.id2label
        
        # Decode tokens and extract entities
        tokens = self.tokenizer.convert_ids_to_tokens(encoded_inputs["input_ids"][0])
        predicted_labels = [id2label.get(pred, "O") for pred in predictions]
        
        # Group tokens into entities
        entities = {}
        current_entity = None
        current_text = []
        
        for token, label in zip(tokens, predicted_labels):
            if token in ["[CLS]", "[SEP]", "[PAD]"]:
                continue
            
            if label.startswith("B-"):
                # Save previous entity if exists
                if current_entity:
                    entity_type = current_entity.replace("B-", "").replace("I-", "")
                    if entity_type not in entities:
                        entities[entity_type] = []
                    entities[entity_type].append(" ".join(current_text))
                
                # Start new entity
                current_entity = label
                current_text = [token.replace("Ġ", " ").strip()]
            
            elif label.startswith("I-") and current_entity and label.replace("I-", "") == current_entity.replace("B-", ""):
                # Continue current entity
                current_text.append(token.replace("Ġ", " ").strip())
            
            else:
                # Save previous entity
                if current_entity:
                    entity_type = current_entity.replace("B-", "").replace("I-", "")
                    if entity_type not in entities:
                        entities[entity_type] = []
                    entities[entity_type].append(" ".join(current_text))
                current_entity = None
                current_text = []
        
        # Save last entity
        if current_entity:
            entity_type = current_entity.replace("B-", "").replace("I-", "")
            if entity_type not in entities:
                entities[entity_type] = []
            entities[entity_type].append(" ".join(current_text))
        
        # Format output
        formatted_lines = []
        if "STORE" in entities:
            formatted_lines.append(f"# {entities['STORE'][0]}")
        
        if "DATE" in entities:
            formatted_lines.append(f"Date: {entities['DATE'][0]}")
        
        if "ITEM" in entities:
            formatted_lines.append("\n## Items")
            for item in entities["ITEM"]:
                formatted_lines.append(f"- {item}")
        
        if "PRICE" in entities:
            formatted_lines.append("\n## Prices")
            for price in entities["PRICE"]:
                formatted_lines.append(f"- {price}")
        
        if "TOTAL" in entities:
            formatted_lines.append(f"\n## Total: {entities['TOTAL'][0]}")
        
        return {
            "entities": entities,
            "formatted_text": "\n".join(formatted_lines) if formatted_lines else "No structured entities detected.",
            "tokens": tokens[:50],  # Limit token output
            "predictions": predicted_labels[:50]  # Limit prediction output
        }

    def predict(
        self,
        image: Path = Input(description="Receipt image"),
        words: List[str] = Input(description="List of words from OCR"),
        boxes: List[List[int]] = Input(description="List of bounding boxes [x0, y0, x1, y1] for each word")
    ) -> Dict:
        """
        Main prediction function called by Replicate.
        
        Args:
            image: Path to receipt image file
            words: List of words extracted by OCR
            boxes: List of bounding boxes [x0, y0, x1, y1] for each word
            
        Returns:
            Dictionary with extracted receipt information
        """
        # Load image
        img = Image.open(image).convert("RGB")
        
        # Process the receipt
        result = self.process_receipt(img, words, boxes)
        
        return result
