# Hugging Face Inference API Setup Guide

## Quick Start

### Step 1: Get Your API Token
1. Go to https://huggingface.co/join and create a free account
2. Go to https://huggingface.co/settings/tokens
3. Click "New token"
4. Name it "ai-chatbot-api"
5. Select "Read" permission
6. Click "Generate token"
7. Copy the token (starts with `hf_...`)

### Step 2: Configure Environment

Create a `.env` file in the `backend` directory:

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your token:

```bash
HF_TOKEN=hf_your_actual_token_here
USE_HUGGINGFACE=true
HF_MODEL_ID=microsoft/Phi-3.5-mini-instruct
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Start the Backend

```bash
cd backend
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
```

You should see:
```
✅ Hugging Face Inference API initialized
   Model: microsoft/Phi-3.5-mini-instruct
   API URL: https://api-inference.huggingface.co/models/microsoft/Phi-3.5-mini-instruct
✅ Hugging Face Inference API activated
```

### Step 5: Test It

```bash
curl http://localhost:8000/health
```

You should see `"model_loaded": true` and the device will be `"huggingface-api"`.

## Alternative: Use Environment Variables Directly

Instead of `.env` file, you can set environment variables:

```bash
export HF_TOKEN="hf_your_token_here"
export USE_HUGGINGFACE=true
cd backend
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
```

## Configuration Options

### Use Different Model
```bash
HF_MODEL_ID=meta-llama/Llama-2-7b-chat-hf USE_HUGGINGFACE=true python3 -m uvicorn app:app ...
```

### Fallback to Mock Engine
If Hugging Face API fails, the system automatically falls back to mock engine.

### Switch Between Engines

**Hugging Face API:**
```bash
USE_HUGGINGFACE=true python3 -m uvicorn app:app ...
```

**Local Model:**
```bash
USE_HUGGINGFACE=false LOAD_MODEL_ON_STARTUP=true python3 -m uvicorn app:app ...
```

**Mock Engine:**
```bash
USE_HUGGINGFACE=false LOAD_MODEL_ON_STARTUP=false python3 -m uvicorn app:app ...
```

## Pricing

- **Free Tier**: 1,000 requests/month
- **After Free Tier**: Pay-as-you-go pricing
- Check current pricing: https://huggingface.co/pricing

## Troubleshooting

### "Hugging Face API token required"
- Make sure you set `HF_TOKEN` in `.env` or as environment variable
- Check that token starts with `hf_`

### "Model is loading, please wait"
- The model needs to be loaded on Hugging Face servers
- Wait a minute and try again
- First request may take longer

### API Errors
- Check your internet connection
- Verify token is valid at https://huggingface.co/settings/tokens
- Check if you've exceeded free tier limits

## Benefits

✅ No local model loading (saves disk space and RAM)
✅ No crashes from memory issues
✅ Fast startup time
✅ Works on any machine with internet
✅ Access to latest models
