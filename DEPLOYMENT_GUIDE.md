# Model Deployment Guide

Your local machine (MacBook with Apple Silicon) cannot efficiently run the Phi-3.5-mini model on CPU. This guide shows you how to deploy your custom fine-tuned model to the cloud for fast inference.

## 🎯 Your Current Situation

- **Model**: Phi-3.5-mini-instruct with custom LoRA adapter (~4GB base + 96MB adapter)
- **Problem**: CPU inference is too slow (60+ seconds timeout)
- **Solution**: Host the model in the cloud with GPU acceleration

---

## 🚀 Recommended Deployment Options

### **Option 1: Hugging Face Inference Endpoints** ⭐ (Recommended)

**Cost**: ~$0.60/hour for GPU (you only pay when it's running)  
**Speed**: ~1-2 seconds per response  
**Difficulty**: Easy

#### Steps:

1. **Upload your model to Hugging Face Hub**
   ```bash
   cd backend
   python3 upload_model_to_hf.py
   ```
   
   This will upload your LoRA adapter to your Hugging Face account.

2. **Deploy as Inference Endpoint**
   - Go to https://huggingface.co/[your-username]/medical-chatbot-phi3-lora
   - Click "Deploy" → "Inference Endpoints"
   - Select: **1x Nvidia T4 GPU** (cheapest option, ~$0.60/hour)
   - Click "Create Endpoint"
   - Wait 2-3 minutes for deployment

3. **Update your backend code**
   - Copy the endpoint URL from Hugging Face
   - Update `backend/.env`:
     ```
     USE_HUGGINGFACE=true
     HF_ENDPOINT_URL=https://[your-endpoint].endpoints.huggingface.cloud
     HF_MODEL_ID=[your-username]/medical-chatbot-phi3-lora
     ```

4. **Modify huggingface_engine.py** to use the endpoint URL

**Pros**:
- ✅ Official, reliable service
- ✅ Fast GPU inference
- ✅ Easy scaling
- ✅ Pay only when running (can pause when not in use)

**Cons**:
- ❌ Costs money (but very affordable for development/testing)

---

### **Option 2: Replicate** 🔄

**Cost**: ~$0.10-0.30 per 1000 requests  
**Speed**: ~1-3 seconds per response  
**Difficulty**: Medium

Replicate allows you to deploy models with pay-per-use pricing.

#### Steps:

1. **Create Replicate account**: https://replicate.com
2. **Push your model**:
   ```bash
   # Install Cog (Replicate's deployment tool)
   brew install replicate/tap/cog
   
   # Create deployment files
   cd backend/ai/model_repo/Ares-chatbot
   # Follow Replicate's guide to create cog.yaml
   ```

3. **Update your backend** to use Replicate API

**Pros**:
- ✅ Pay per use (cheaper for low traffic)
- ✅ No idle costs
- ✅ Easy to use

**Cons**:
- ❌ Cold start latency (first request after idle is slower)

---

### **Option 3: Modal Labs** ⚡

**Cost**: ~$0.10 per GPU hour  
**Speed**: ~1-2 seconds per response  
**Difficulty**: Medium

Modal provides serverless GPU hosting.

#### Steps:

1. **Install Modal**:
   ```bash
   pip install modal
   ```

2. **Create deployment script** (I can help you create this)

3. **Deploy**:
   ```bash
   modal deploy
   ```

**Pros**:
- ✅ Serverless (auto-scales to zero)
- ✅ Very affordable
- ✅ Fast cold starts

**Cons**:
- ❌ Requires some code changes

---

### **Option 4: RunPod** 💰

**Cost**: ~$0.20-0.50/hour for GPU  
**Speed**: ~1-2 seconds per response  
**Difficulty**: Medium-Hard

RunPod offers cheap GPU rentals.

#### Steps:

1. Sign up at https://runpod.io
2. Create a pod with GPU (RTX 3090 or similar)
3. Deploy your model as API endpoint
4. Point your backend to RunPod URL

**Pros**:
- ✅ Cheaper than Hugging Face
- ✅ More GPU options

**Cons**:
- ❌ More setup required
- ❌ Less reliable than managed services

---

### **Option 5: Google Colab Pro** 🎓 (Development Only)

**Cost**: $10/month  
**Speed**: ~2-3 seconds per response  
**Difficulty**: Easy

Use Google Colab's free/Pro tier GPU for development.

#### Steps:

1. Upload your model to Google Drive
2. Create a Colab notebook that:
   - Loads your model
   - Exposes an API endpoint using ngrok
3. Point your backend to the ngrok URL

**Pros**:
- ✅ Very cheap ($10/month unlimited)
- ✅ Good for testing

**Cons**:
- ❌ Sessions disconnect after inactivity
- ❌ Not suitable for production
- ❌ Unreliable

---

## 📊 Quick Comparison

| Service | Cost/Hour | Setup Difficulty | Reliability | Best For |
|---------|-----------|------------------|-------------|----------|
| **HF Endpoints** | $0.60 | ⭐ Easy | ⭐⭐⭐ High | Production, Demos |
| **Replicate** | Pay/use | ⭐⭐ Medium | ⭐⭐⭐ High | Low-traffic apps |
| **Modal Labs** | $0.10 | ⭐⭐ Medium | ⭐⭐ Medium | Serverless apps |
| **RunPod** | $0.30 | ⭐⭐⭐ Hard | ⭐⭐ Medium | Budget-conscious |
| **Colab Pro** | $10/mo | ⭐ Easy | ⭐ Low | Development only |

---

## 🎯 My Recommendation for You

**Start with Hugging Face Inference Endpoints** because:

1. ✅ Easiest setup (just run the upload script)
2. ✅ Most reliable and well-documented
3. ✅ You already have HF_TOKEN configured
4. ✅ Can pause when not in use (pay only for active hours)
5. ✅ Professional service, good for demos and production

**Estimated costs**:
- Development (2 hours/day): ~$1.20/day = $36/month
- Testing only (1 hour/day): ~$0.60/day = $18/month
- Always-on production: ~$432/month

**Money-saving tip**: 
- Pause the endpoint when not in use
- Only turn it on when you're actively testing/demoing

---

## 🛠️ Quick Start: Deploy to Hugging Face Now

Run this command to upload your model:

```bash
cd backend
python3 upload_model_to_hf.py
```

Then follow the instructions printed by the script to deploy as an Inference Endpoint.

---

## 🤔 Still Have Questions?

Let me know which option you'd like to pursue and I can help you set it up!
