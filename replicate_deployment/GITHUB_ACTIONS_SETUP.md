# Complete Guide: Connect Replicate to GitHub

## ✅ Your Code is Already on GitHub!
Repository: https://github.com/whidge/layoutlmv3-cord-receipts

## Method: GitHub Actions (Recommended)

Replicate uses GitHub Actions to build and deploy models. Here's how to set it up:

### Step 1: Get Your Replicate Token

1. Go to: https://replicate.com/account/api-tokens
2. Copy your **CLI authentication token**
3. It looks like: `r8_xxxxxxxxxxxxxxxxxxxxx`

### Step 2: Add Token to GitHub Secrets

1. Go to your GitHub repository: https://github.com/whidge/layoutlmv3-cord-receipts
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `REPLICATE_CLI_AUTH_TOKEN`
5. Value: Paste your Replicate token
6. Click **Add secret**

### Step 3: Trigger the Workflow

**Option A: Manual Trigger**
1. Go to: https://github.com/whidge/layoutlmv3-cord-receipts/actions
2. Click **"Push to Replicate"** workflow
3. Click **"Run workflow"**
4. Enter model name: `whidge/layoutlmv3-cord-receipts`
5. Click **"Run workflow"**

**Option B: Automatic on Push**
- The workflow will automatically run when you push changes to `replicate_deployment/`
- Just push your code and it will build automatically!

### Step 4: Monitor Build

1. Watch the build progress in GitHub Actions tab
2. Check your Replicate model page: https://replicate.com/whidge/layoutlmv3-cord-receipts
3. Build takes 10-20 minutes

## What Happens

1. GitHub Actions clones your repo
2. Sets up Cog (Replicate's build tool)
3. Builds Docker image on GitHub's servers
4. Pushes to Replicate
5. Your model is live!

## Files Created

✅ `.github/workflows/deploy.yml` - GitHub Actions workflow
✅ `replicate_deployment/` - All your model files

## Next Steps

1. **Get Replicate token**: https://replicate.com/account/api-tokens
2. **Add to GitHub Secrets**: Repository → Settings → Secrets
3. **Trigger workflow**: Actions → Run workflow
4. **Wait for build**: 10-20 minutes
5. **Test your model**: https://replicate.com/whidge/layoutlmv3-cord-receipts

## Troubleshooting

**Workflow fails?**
- Check token is correct in GitHub Secrets
- Verify model name matches: `whidge/layoutlmv3-cord-receipts`
- Check workflow logs in Actions tab

**Build fails?**
- Check `cog.yaml` syntax
- Verify all dependencies are listed
- Check build logs in GitHub Actions

**Model not appearing?**
- Make sure model exists: https://replicate.com/create
- Verify model name matches exactly

