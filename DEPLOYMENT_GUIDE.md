# DeepSeekOCR + LayoutLMv3 Deployment Guide

## Overview

This setup deploys two separate Replicate models:
1. **DeepSeekOCR**: Extracts text from images
2. **LayoutLMv3**: Processes OCR results to extract structured receipt entities

## Step-by-Step Deployment via GitHub Actions (Recommended)

### Prerequisites

- Replicate account: https://replicate.com
- Replicate API token: https://replicate.com/account/api-tokens
- GitHub repository with code pushed

### Step 1: Set Up GitHub Secrets

1. Go to your GitHub repository: https://github.com/whidge/layoutlmv3-cord-receipts
2. Navigate to: Settings → Secrets and variables → Actions
3. Add a new secret:
   - Name: `REPLICATE_CLI_AUTH_TOKEN`
   - Value: Your Replicate API token

### Step 2: Create GitHub Actions Workflows

Create two workflow files in `.github/workflows/`:

**`.github/workflows/deploy-deepseekocr.yml`:**
```yaml
name: Deploy DeepSeekOCR to Replicate

on:
  workflow_dispatch:
    inputs:
      model_name:
        description: 'Model name (e.g., whidge/deepseekocr)'
        required: true
        default: 'whidge/deepseekocr'
  push:
    branches:
      - main
    paths:
      - 'replicate_deployment/deepseekocr/**'
      - '.github/workflows/deploy-deepseekocr.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    name: Build and push DeepSeekOCR to Replicate
    steps:
      - name: Free disk space
        uses: jlumbroso/free-disk-space@v1.3.1
        with:
          tool-cache: false
          docker-images: false

      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Cog
        uses: replicate/setup-cog@v2
        with:
          token: ${{ secrets.REPLICATE_CLI_AUTH_TOKEN }}

      - name: Build and push DeepSeekOCR to Replicate
        working-directory: replicate_deployment/deepseekocr
        run: |
          echo "🚀 Building and pushing DeepSeekOCR to Replicate..."
          MODEL_NAME="${{ github.event.inputs.model_name || 'whidge/deepseekocr' }}"
          echo "Model: r8.im/${MODEL_NAME}"
          
          MAX_RETRIES=3
          RETRY_COUNT=0
          
          while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
            if cog push "r8.im/${MODEL_NAME}"; then
              echo "✅ Successfully deployed DeepSeekOCR to Replicate!"
              exit 0
            else
              RETRY_COUNT=$((RETRY_COUNT + 1))
              if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                echo "⚠️ Push failed, retrying in 30 seconds... (Attempt $RETRY_COUNT/$MAX_RETRIES)"
                sleep 30
              else
                echo "❌ Failed after $MAX_RETRIES attempts"
                exit 1
              fi
            fi
          done
```

**`.github/workflows/deploy-layoutlmv3.yml`:**
```yaml
name: Deploy LayoutLMv3 to Replicate

on:
  workflow_dispatch:
    inputs:
      model_name:
        description: 'Model name (e.g., whidge/layoutlmv3-receipts)'
        required: true
        default: 'whidge/layoutlmv3-receipts'
  push:
    branches:
      - main
    paths:
      - 'replicate_deployment/layoutlmv3/**'
      - '.github/workflows/deploy-layoutlmv3.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    name: Build and push LayoutLMv3 to Replicate
    steps:
      - name: Free disk space
        uses: jlumbroso/free-disk-space@v1.3.1
        with:
          tool-cache: false
          docker-images: false

      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Cog
        uses: replicate/setup-cog@v2
        with:
          token: ${{ secrets.REPLICATE_CLI_AUTH_TOKEN }}

      - name: Build and push LayoutLMv3 to Replicate
        working-directory: replicate_deployment/layoutlmv3
        run: |
          echo "🚀 Building and pushing LayoutLMv3 to Replicate..."
          MODEL_NAME="${{ github.event.inputs.model_name || 'whidge/layoutlmv3-receipts' }}"
          echo "Model: r8.im/${MODEL_NAME}"
          
          MAX_RETRIES=3
          RETRY_COUNT=0
          
          while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
            if cog push "r8.im/${MODEL_NAME}"; then
              echo "✅ Successfully deployed LayoutLMv3 to Replicate!"
              exit 0
            else
              RETRY_COUNT=$((RETRY_COUNT + 1))
              if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                echo "⚠️ Push failed, retrying in 30 seconds... (Attempt $RETRY_COUNT/$MAX_RETRIES)"
                sleep 30
              else
                echo "❌ Failed after $MAX_RETRIES attempts"
                exit 1
              fi
            fi
          done
```

### Step 3: Push to GitHub and Trigger Deployment

```bash
# Add and commit the new files
git add replicate_deployment/deepseekocr replicate_deployment/layoutlmv3 .github/workflows/
git commit -m "Add DeepSeekOCR and LayoutLMv3 models with GitHub Actions"
git push origin main
```

### Step 4: Trigger Workflows

1. Go to: https://github.com/whidge/layoutlmv3-cord-receipts/actions
2. Click on "Deploy DeepSeekOCR to Replicate" workflow
3. Click "Run workflow" → "Run workflow"
4. Repeat for "Deploy LayoutLMv3 to Replicate"

Or push changes to trigger automatic deployment:
- Changes to `replicate_deployment/deepseekocr/**` trigger DeepSeekOCR deployment
- Changes to `replicate_deployment/layoutlmv3/**` trigger LayoutLMv3 deployment

Wait for builds to complete (10-20 minutes each).

### Step 3: Update Client Script

Edit `client.py` and replace:
- `YOUR_USERNAME/deepseekocr` with your actual DeepSeekOCR model name
- `YOUR_USERNAME/layoutlmv3-receipts` with your actual LayoutLMv3 model name

### Step 4: Install Client Dependencies

```bash
pip install -r requirements_client.txt
```

### Step 5: Set API Token

```bash
export REPLICATE_API_TOKEN=your_token_here
```

### Step 6: Test the Pipeline

```bash
python client.py path/to/receipt.jpg
```

## File Structure

```
replicate_deployment/
├── deepseekocr/
│   ├── cog.yaml          # DeepSeekOCR configuration
│   ├── predict.py        # DeepSeekOCR prediction logic
│   └── requirements.txt  # DeepSeekOCR dependencies
├── layoutlmv3/
│   ├── cog.yaml          # LayoutLMv3 configuration
│   ├── predict.py        # LayoutLMv3 prediction logic
│   └── requirements.txt  # LayoutLMv3 dependencies
└── (existing files...)

client.py                  # Local client to chain both models
requirements_client.txt    # Client dependencies
```

## Model Inputs/Outputs

### DeepSeekOCR
- **Input**: Image file
- **Output**: `{"text": "extracted text..."}`

### LayoutLMv3
- **Input**: 
  - `image`: Receipt image file
  - `words`: List of words from OCR
  - `boxes`: List of bounding boxes [x0, y0, x1, y1] for each word
- **Output**: 
  - `entities`: Dictionary with STORE, DATE, ITEM, PRICE, TOTAL
  - `formatted_text`: Formatted receipt text

## Notes

- The client script estimates bounding boxes from OCR text. For better accuracy, consider using an OCR that provides actual bounding boxes.
- Both models require GPU (configured in cog.yaml).
- Build times: ~10-20 minutes per model.
- First run may be slower due to model downloads.

## Troubleshooting

- **Build fails**: Check build logs on Replicate dashboard
- **API errors**: Verify REPLICATE_API_TOKEN is set correctly
- **Model not found**: Ensure model names match exactly (case-sensitive)

