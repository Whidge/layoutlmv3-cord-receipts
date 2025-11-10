"""Replicate prediction script for DeepSeekOCR."""

import torch
from PIL import Image
from typing import Dict
from transformers import DeepseekVLHybridForConditionalGeneration, AutoProcessor
from cog import BasePredictor, Input, Path


class Predictor(BasePredictor):
    """Cog Predictor class for DeepSeekOCR."""
    
    def setup(self):
        """Load model components once at startup."""
        print("Loading DeepSeekOCR model...")
        
        model_name = "deepseek-ai/DeepSeek-OCR"
        
        # Load processor and model
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = DeepseekVLHybridForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.model.eval()
        
        print("DeepSeekOCR model loaded successfully")
    
    def predict(self, image: Path = Input(description="Image to extract text from")) -> Dict:
        """
        Extract text from image using DeepSeekOCR.
        
        Args:
            image: Path to image file
            
        Returns:
            Dictionary with extracted text
        """
        # Load image
        img = Image.open(image).convert("RGB")
        
        # Prepare messages for the model
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": img},
                    {"type": "text", "text": "Extract all text from this image. Return only the text content, no additional explanation."}
                ]
            }
        ]
        
        # Process inputs
        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        ).to(self.model.device, dtype=self.model.dtype)
        
        # Generate text
        with torch.no_grad():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=2048,
                do_sample=False
            )
        
        # Decode output
        generated_ids_trimmed = [
            out_ids[len(in_ids):] 
            for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        output_text = self.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]
        
        return {
            "text": output_text.strip()
        }
