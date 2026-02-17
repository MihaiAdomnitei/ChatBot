# 🚀 Use Your Model on Google Colab (FREE!)

Since you don't have the "Deploy" button (requires payment), use Google Colab instead - it's FREE and gives you GPU access!

## ⚡ Quick Start (5 minutes)

### Step 1: Open Google Colab
Go to: https://colab.research.google.com

### Step 2: Enable FREE GPU
1. Click **Runtime** (top menu)
2. Click **Change runtime type**
3. Select **T4 GPU** (it's free!)
4. Click **Save**

### Step 3: Copy & Paste These Cells

I've created the code for you in `colab_notebook.py`. Just copy each section into a new cell:

---

## 📱 CELL 1: Install Packages

```python
!pip install -q transformers accelerate peft torch
```

**Run this first** (takes ~30 seconds)

---

## 🤖 CELL 2: Load Your Model

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

print("🔄 Loading base model...")
model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Phi-3.5-mini-instruct",
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)

print("🔄 Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    "microsoft/Phi-3.5-mini-instruct",
    use_fast=True,
    trust_remote_code=True
)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("🔄 Loading YOUR LoRA adapter...")
model = PeftModel.from_pretrained(model, "mihAAI19/medical-chatbot-phi3-lora")
model = model.merge_and_unload()
model.eval()

print("✅ Your custom model loaded successfully!")
print(f"   Device: {model.device}")
if torch.cuda.is_available():
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
```

**Wait ~2 minutes** for first load (downloads model)

---

## 💬 CELL 3: Chat Function

```python
def chat(user_message, max_new_tokens=100):
    messages = [{"role": "user", "content": user_message}]
    
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.4,
            top_p=0.9,
            repetition_penalty=1.1,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id
        )
    
    generated_tokens = outputs[0, inputs["input_ids"].shape[-1]:]
    response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    return response.strip()

print("✅ Chat function ready!")
```

---

## 🧪 CELL 4: Test It!

```python
# Test your model
question = "I have tooth pain when eating cold food. What could this be?"
print(f"Question: {question}")
response = chat(question)
print(f"Response: {response}")
```

**That's it!** Your model is now running on free GPU! 🎉

---

## 🌐 Want to Connect Colab to Your FastAPI Backend?

Run this **optional** Cell 5:

```python
!pip install -q fastapi uvicorn pyngrok nest-asyncio

from fastapi import FastAPI
from pydantic import BaseModel
from pyngrok import ngrok
import nest_asyncio
import uvicorn

nest_asyncio.apply()

app = FastAPI()

class GenerateRequest(BaseModel):
    inputs: str
    parameters: dict = {}

@app.post("/generate")
def generate(request: GenerateRequest):
    prompt = request.inputs
    max_tokens = request.parameters.get("max_new_tokens", 100)
    
    inputs_tensor = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.inference_mode():
        outputs = model.generate(
            **inputs_tensor,
            max_new_tokens=max_tokens,
            temperature=0.4,
            top_p=0.9
        )
    
    generated_tokens = outputs[0, inputs_tensor["input_ids"].shape[-1]:]
    text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
    
    return [{"generated_text": text}]

@app.get("/health")
def health():
    return {"status": "ok"}

# Get public URL
public_url = ngrok.connect(8000)
print(f"\n✅ Public URL: {public_url}")
print(f"\nAdd to backend/.env:")
print(f"HF_ENDPOINT_URL={public_url}/generate")

# Start server
uvicorn.run(app, host="0.0.0.0", port=8000)
```

Then update your `backend/.env`:
```env
HF_ENDPOINT_URL=https://xxxxx.ngrok.io/generate
```

**⚠️ Important**: The Colab session disconnects after ~12 hours of inactivity!

---

## 📊 Comparison

| Option | Cost | Speed | Your Model | Always On |
|--------|------|-------|------------|-----------|
| **Current (Free HF API)** | FREE | 3-10s | ❌ No | ✅ Yes |
| **Google Colab** | FREE | 1-3s | ✅ Yes | ❌ No (disconnects) |
| **HF Endpoint** | $0.60/hr | 1-2s | ✅ Yes | ✅ Yes |

---

## 🎯 My Recommendation

**For Development/Testing:**
Use **Google Colab** (free, fast, your custom model)

**For Production:**
Stick with **current setup** (free, always on) OR pay for **HF Endpoint** (fast, always on, your model)

---

## ✅ Next Steps

1. Open Google Colab: https://colab.research.google.com
2. Enable GPU (Runtime → Change runtime type → T4 GPU)
3. Copy cells 1-4 above
4. Test your model!

**Need help?** Just ask! 🚀
