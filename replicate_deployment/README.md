# Deploying LayoutLMv3 to Replicate

This guide will help you deploy the LayoutLMv3 CORD model to your Replicate dashboard.

## Prerequisites

1. **Replicate Account**: Sign up at [replicate.com](https://replicate.com)
2. **Replicate CLI**: Install it with `pip install replicate`
3. **Docker**: Make sure Docker is installed and running

## Step-by-Step Deployment

### 1. Install Replicate CLI

```bash
pip install replicate
```

### 2. Authenticate with Replicate

```bash
replicate login
```

This will open a browser window for you to authenticate.

### 3. Create a New Model

In your Replicate dashboard:
- Go to "Models" → "Create Model"
- Choose a name (e.g., `your-username/layoutlmv3-cord-receipts`)
- Set visibility (public or private)
- **Select Hardware** (see Hardware Recommendations below)

### 4. Navigate to Deployment Directory

```bash
cd replicate_deployment
```

### 5. Initialize Replicate Model (if not done via dashboard)

```bash
replicate init
```

Follow the prompts to create your model.

### 6. Build and Push to Replicate

```bash
# Build and push the model
replicate push
```

This will:
- Build the Docker image
- Upload it to Replicate
- Make it available in your dashboard

### 7. Test Your Model

Once deployed, you can test it:

**Via Python:**
```python
import replicate

output = replicate.run(
    "your-username/layoutlmv3-cord-receipts:latest",
    input={"image": "https://example.com/receipt.jpg"}
)

print(output)
```

**Via Replicate Dashboard:**
- Go to your model page
- Click "Run" tab
- Upload a receipt image
- See the results

## Model Input/Output

### Input
- `image`: Receipt image (URL, file path, or image data)

### Output
```json
{
  "entities": {
    "STORE": ["Store Name"],
    "DATE": ["2024-01-01"],
    "ITEM": ["Item 1", "Item 2"],
    "PRICE": ["$10.00", "$20.00"],
    "TOTAL": ["$30.00"]
  },
  "formatted_text": "# Store Name\nDate: 2024-01-01\n...",
  "tokens": [...],
  "predictions": [...]
}
```

## Troubleshooting

### Model Loading Issues
- Check that all dependencies are in `requirements.txt`
- Verify the model names are correct in `predict.py`

### OCR Issues
- EasyOCR requires GPU for best performance
- If OCR fails, check Docker logs: `replicate logs <model-name>`

### Build Issues
- Make sure Docker is running
- Check Dockerfile syntax
- Verify all file paths are correct

## Customization

### Change Model
Edit `predict.py` and change:
```python
MODEL_NAME = "nielsr/layoutlmv3-finetuned-cord"
```

### Add More OCR Engines
You can modify `extract_text_with_boxes()` to use different OCR libraries.

### Adjust Output Format
Modify the `process_receipt()` function to change how entities are formatted.

## Hardware Recommendations

When creating your model in Replicate, you'll be asked to select hardware. Here are recommendations:

### ✅ Recommended: **Nvidia T4 GPU**
- **Best balance** of cost and performance
- Sufficient for LayoutLMv3 + EasyOCR inference
- Good for most production use cases
- Lower cost per second

### ⚡ Faster Option: **Nvidia L40S GPU**
- Faster inference times
- Better for high-throughput scenarios
- Higher cost but better performance

### 🚀 Maximum Performance: **Nvidia A100 (80GB) or H100**
- Fastest inference (2-3x faster than T4)
- Best for low-latency requirements
- Highest cost - only use if speed is critical

### ❌ Avoid: **CPU**
- Too slow for LayoutLMv3 (10-30x slower)
- EasyOCR is much slower on CPU
- Not recommended for production

### Memory Considerations
- LayoutLMv3 base model: ~500MB
- EasyOCR models: ~200MB
- Total: ~1GB+ GPU memory needed
- **T4 (16GB)** is sufficient
- **L40S (48GB)** has plenty of headroom

## Cost Considerations

- Replicate charges per second of GPU time
- LayoutLMv3 is a large model (~500MB)
- First run may be slower due to model download
- **T4**: Most cost-effective for this workload
- **L40S/A100**: Faster but more expensive
- Typical inference time: 2-5 seconds on T4, 1-3 seconds on L40S

## Next Steps

1. Test with various receipt images
2. Monitor usage and costs in Replicate dashboard
3. Optimize model if needed (quantization, smaller model)
4. Set up webhooks for production use

