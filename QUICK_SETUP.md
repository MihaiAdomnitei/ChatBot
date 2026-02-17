# Quick Setup Guide: Deploy Your Model

This guide will help you deploy your custom medical chatbot model to Hugging Face so you can use it without the slow CPU inference.

## 📋 Prerequisites

- ✅ Hugging Face account (you already have one)
- ✅ HF_TOKEN in your `.env` file (already configured)
- ✅ Your model in `backend/ai/model_repo/Ares-chatbot`

## 🚀 Step 1: Upload Model to Hugging Face

Run the upload script:

```bash
cd backend
python3 upload_model_to_hf.py
```

This will:
- Upload your LoRA adapter (~96MB) to Hugging Face Hub
- Create a public repository under your account
- Print next steps

Expected output:
```
✅ Successfully uploaded to Hugging Face!

📋 Next steps:
   1. View your model: https://huggingface.co/[your-username]/medical-chatbot-phi3-lora
   ...
```

## 🎯 Step 2: Choose Your Deployment Option

### Option A: Free Inference API (Current Setup) ⭐

**Current status**: Already working!  
**Speed**: Moderate (3-10 seconds per response)  
**Cost**: FREE (with rate limits)

Your app is already configured for this. Just keep:
```env
USE_HUGGINGFACE=true
LOAD_MODEL_ON_STARTUP=false
HF_MODEL_ID=microsoft/Phi-3.5-mini-instruct
```

**Note**: The free API uses the base Phi-3.5 model WITHOUT your custom LoRA adapter. For your custom fine-tuned model, use Option B.

---

### Option B: Dedicated Inference Endpoint (Recommended for Custom Model) 💰

**Speed**: Fast (1-2 seconds per response)  
**Cost**: ~$0.60/hour (pause when not in use)

#### Steps:

1. **Go to your model page**:
   After upload, visit: `https://huggingface.co/[your-username]/medical-chatbot-phi3-lora`

2. **Deploy Inference Endpoint**:
   - Click "Deploy" button (top right)
   - Select "Inference Endpoints"
   - Choose settings:
     - **Instance**: GPU [medium] - 1x Nvidia T4
     - **Region**: US East (cheapest)
     - **Auto-scaling**: Min 0, Max 1 (to pause when idle)
   - Click "Create Endpoint"

3. **Wait for deployment** (2-3 minutes)
   Status will change: `Building` → `Running`

4. **Copy the endpoint URL**:
   It will look like: `https://xxxxxx.us-east-1.aws.endpoints.huggingface.cloud`

5. **Update your `.env` file**:
   ```env
   USE_HUGGINGFACE=true
   HF_ENDPOINT_URL=https://xxxxxx.us-east-1.aws.endpoints.huggingface.cloud
   HF_MODEL_ID=[your-username]/medical-chatbot-phi3-lora
   LOAD_MODEL_ON_STARTUP=false
   ```

6. **Restart your backend**:
   ```bash
   # Stop current server (Ctrl+C)
   cd backend
   python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
   ```

7. **Test it!**
   Send a message - it should respond in 1-2 seconds now!

#### Cost Management Tips:

**Pause when not in use**:
- Go to your endpoint dashboard
- Click "Pause" button
- Restart when needed (takes ~1 minute to resume)

**Auto-pause** (recommended):
- Enable "Scale to Zero" in endpoint settings
- Endpoint automatically pauses after 15 minutes of no requests
- First request after pause takes ~60 seconds (cold start)
- Subsequent requests are fast

**Expected costs**:
- Active testing (2 hours/day): ~$36/month
- With auto-pause: ~$10-20/month
- Always-on: ~$432/month

---

## 🧪 Step 3: Test Your Setup

### Test with curl:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test creating a chat
curl -X POST http://localhost:8000/chats \
  -H "Content-Type: application/json" \
  -d '{"pathology": "dental_caries"}'

# Test sending a message (replace CHAT_ID)
curl -X POST http://localhost:8000/chats/CHAT_ID/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I have tooth pain"}'
```

### Check server logs:

You should see:
```
✅ Hugging Face Inference Endpoint initialized
   Endpoint: https://xxxxx.endpoints.huggingface.cloud
```

---

## 📊 Comparing Your Options

| Option | Speed | Cost | Custom Model | Setup |
|--------|-------|------|--------------|-------|
| **Current (Free API)** | Moderate | FREE | ❌ No | ✅ Done |
| **Dedicated Endpoint** | Fast | $0.60/hr | ✅ Yes | 5 minutes |
| **Local CPU** | Very Slow | FREE | ✅ Yes | Doesn't work |

---

## 🔍 Troubleshooting

### Upload fails with "403 Forbidden":
- Check your HF_TOKEN is valid
- Go to https://huggingface.co/settings/tokens
- Create a new token with "Write" permission

### Endpoint returns 503:
- Endpoint is still loading (wait 1-2 minutes)
- Or endpoint is paused (resume from dashboard)

### Endpoint returns 401:
- Check HF_TOKEN in .env is correct
- Token needs "Read" permission for endpoints

### Still getting timeout errors:
- Verify HF_ENDPOINT_URL is set correctly in .env
- Check endpoint status in Hugging Face dashboard
- Ensure endpoint is "Running" (green status)

---

## 💡 Recommended Path for You

1. ✅ **Keep using free API for now** (already working)
2. 📤 **Upload your model** when you have time: `python3 upload_model_to_hf.py`
3. 🚀 **Deploy endpoint** when you need:
   - Your custom fine-tuned responses
   - Faster performance
   - More control

The free API is good enough for development and testing!

---

## 🆘 Need Help?

Just ask me! I can help you with:
- Uploading the model
- Deploying the endpoint
- Debugging errors
- Cost optimization
- Alternative hosting options
