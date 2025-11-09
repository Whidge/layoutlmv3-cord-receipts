#!/bin/bash
# Deployment script for LayoutLMv3 to Replicate

echo "🚀 Deploying LayoutLMv3 to Replicate"
echo "======================================"
echo ""

# Step 1: Install Cog CLI (if not already installed)
echo "Step 1: Installing Cog CLI..."
if ! command -v cog &> /dev/null; then
    echo "Cog not found. Installing..."
    # Install to local bin
    mkdir -p ~/.local/bin
    curl -o ~/.local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_$(uname -s)_$(uname -m)
    chmod +x ~/.local/bin/cog
    export PATH="$HOME/.local/bin:$PATH"
    echo "✅ Cog installed to ~/.local/bin/cog"
    echo "   Add this to your ~/.zshrc: export PATH=\"\$HOME/.local/bin:\$PATH\""
else
    echo "✅ Cog already installed"
fi

echo ""
echo "Step 2: Login to Replicate"
echo "---------------------------"
echo "You'll need to login. Run this command:"
echo "  cog login"
echo ""
echo "This will open a browser for authentication."
echo ""

read -p "Have you logged in? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please run 'cog login' first, then run this script again."
    exit 1
fi

echo ""
echo "Step 3: Create Model on Replicate Dashboard"
echo "--------------------------------------------"
echo "1. Go to https://replicate.com/create"
echo "2. Create a new model (e.g., 'your-username/layoutlmv3-cord-receipts')"
echo "3. Select hardware: Nvidia T4 GPU (recommended)"
echo "4. Set visibility (public/private)"
echo ""

read -p "Enter your model name (format: username/model-name): " MODEL_NAME

if [ -z "$MODEL_NAME" ]; then
    echo "Error: Model name is required"
    exit 1
fi

echo ""
echo "Step 4: Building and Pushing Model"
echo "-----------------------------------"
echo "This will take several minutes..."
echo ""

cd "$(dirname "$0")"
cog build -t "$MODEL_NAME"
cog push "r8.im/$MODEL_NAME"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Your model is available at: https://replicate.com/$MODEL_NAME"
echo ""
echo "Test it with:"
echo "  python -c \"import replicate; print(replicate.run('$MODEL_NAME:latest', input={'image': 'path/to/receipt.jpg'}))\""

