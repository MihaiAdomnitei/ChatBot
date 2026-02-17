# Google Colab Setup Guide

Complete guide to run your medical chatbot model on Google Colab with free GPU.

---

## 🚀 Complete Colab Notebook Code

Copy and paste these cells in order:

### Cell 1: Install Dependencies

```python
# Install required packages
!pip install -q transformers accelerate peft torch bitsandbytes
```

---

### Cell 2: Load Model and Adapter

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Model configuration
BASE_MODEL_ID = "microsoft/Phi-3.5-mini-instruct"
ADAPTER_MODEL_ID = "mihAAI19/medical-chatbot-phi3-lora"

print("🔄 Loading base model...")
# Load base model
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto",  # Automatically uses GPU if available
    trust_remote_code=True
)

print("🔄 Loading tokenizer...")
# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL_ID,
    use_fast=True,
    trust_remote_code=True
)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("🔄 Loading LoRA adapter...")
# Load and merge LoRA adapter
model = PeftModel.from_pretrained(model, ADAPTER_MODEL_ID)
model = model.merge_and_unload()
model.eval()

print("✅ Model loaded successfully!")
print(f"   Device: {model.device}")
print(f"   Memory allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
```

---

### Cell 3: Test Generation (Simple)

```python
# Simple test
question = "What are the common symptoms of a cold?"

# Tokenize input
inputs = tokenizer(question, return_tensors="pt").to(model.device)

# Generate response
print("🤖 Generating response...")
with torch.inference_mode():
    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        do_sample=True,
        temperature=0.4,
        top_p=0.9,
        repetition_penalty=1.1
    )

# Decode and print
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("\n" + "="*60)
print("RESPONSE:")
print("="*60)
print(response)
```

---

### Cell 4: Chat Function (Recommended)

```python
def chat(messages, max_new_tokens=100):
    """
    Generate a response using the medical chatbot.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
                  Example: [{"role": "user", "content": "I have a toothache"}]
        max_new_tokens: Maximum tokens to generate
    
    Returns:
        Generated response text
    """
    # Format messages using chat template
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate
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
    
    # Extract only the generated tokens (remove the prompt)
    generated_tokens = outputs[0, inputs["input_ids"].shape[-1]:]
    response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    
    return response.strip()

# Test the chat function
print("✅ Chat function ready!")
print("\nExample usage:")
print("="*60)

messages = [
    {"role": "user", "content": "I have tooth pain when eating cold food. What could this be?"}
]

response = chat(messages)
print(f"User: {messages[0]['content']}")
print(f"\nAssistant: {response}")
```

---

### Cell 5: Interactive Chat Session

```python
# Interactive chat with conversation history
conversation = []

def chat_interactive(user_message):
    """Add user message and get bot response"""
    # Add user message to conversation
    conversation.append({"role": "user", "content": user_message})
    
    # Generate response
    response = chat(conversation, max_new_tokens=150)
    
    # Add assistant response to conversation
    conversation.append({"role": "assistant", "content": response})
    
    return response

# Example conversation
print("🤖 Medical Chatbot - Interactive Session")
print("="*60)

# First message
user_msg = "Hello, I have been experiencing tooth sensitivity."
print(f"\n👤 You: {user_msg}")
bot_response = chat_interactive(user_msg)
print(f"🤖 Bot: {bot_response}")

# Follow-up message
user_msg = "It's worse with cold drinks. What should I do?"
print(f"\n👤 You: {user_msg}")
bot_response = chat_interactive(user_msg)
print(f"🤖 Bot: {bot_response}")

# View full conversation
print("\n" + "="*60)
print("FULL CONVERSATION:")
print("="*60)
for msg in conversation:
    role = "👤 You" if msg["role"] == "user" else "🤖 Bot"
    print(f"{role}: {msg['content']}\n")
```

---

### Cell 6: System Prompt for Medical Simulation

```python
# Use with system prompt for better medical simulation
def create_patient_chat(pathology, chief_complaint):
    """
    Create a patient simulation chat with system prompt.
    
    Args:
        pathology: The medical condition to simulate
        chief_complaint: Main symptom/complaint
    """
    system_prompt = f"""You are simulating a patient with {pathology}.
Chief complaint: {chief_complaint}

Instructions:
- Answer questions as if you are the patient
- Describe symptoms realistically
- Don't diagnose yourself
- Be brief and natural
- Only share information when asked"""
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    return messages

# Example: Dental caries patient
patient_messages = create_patient_chat(
    pathology="dental caries (tooth cavity)",
    chief_complaint="Tooth pain when eating sweets"
)

# Add doctor's question
patient_messages.append({
    "role": "user",
    "content": "Hello, what brings you in today?"
})

# Get patient's response
response = chat(patient_messages, max_new_tokens=80)
print("🏥 Patient Simulation - Dental Caries")
print("="*60)
print(f"👨‍⚕️ Doctor: Hello, what brings you in today?")
print(f"🤕 Patient: {response}")
```

---

## 💡 Tips for Using in Colab

### Enable GPU (Important!)

1. Click **Runtime** → **Change runtime type**
2. Select **GPU** (T4 is free)
3. Click **Save**
4. You'll get much faster generation!

### Check GPU Status

```python
# Check if GPU is available
print(f"GPU available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
```

### Memory Management

```python
# Clear GPU memory if needed
import gc
torch.cuda.empty_cache()
gc.collect()
```

---

## 🐛 Troubleshooting

### Error: "name 'model' is not defined"
**Solution**: Run Cell 2 first to load the model

### Error: "CUDA out of memory"
**Solutions**:
1. Reduce `max_new_tokens` to 50-100
2. Use smaller batch size
3. Restart runtime and run cells again
4. Use float16: `torch_dtype=torch.float16`

### Model loading is slow
**This is normal**:
- First time: 2-5 minutes (downloads model)
- Subsequent runs: 30-60 seconds (uses cached model)

### Generation is slow
**Solutions**:
1. Make sure GPU is enabled (Runtime → Change runtime type → GPU)
2. Reduce `max_new_tokens`
3. Check GPU usage: `!nvidia-smi`

---

## 📊 Expected Performance

| Setup | Load Time | Generation Speed | Cost |
|-------|-----------|------------------|------|
| Colab Free (GPU) | 1-2 min | 1-3 sec/response | FREE |
| Colab Pro (Better GPU) | 1-2 min | 0.5-1 sec/response | $10/month |
| Colab Free (CPU) | 2-3 min | 30-60 sec/response | FREE but slow |

---

## 🚀 Quick Start

**Just want to test it quickly?** Run these 3 cells:

1. **Cell 1**: Install dependencies
2. **Cell 2**: Load model
3. **Cell 4**: Test chat function

That's it! You can start chatting with your model.

---

## 💻 Connect Colab to Your Backend

Want to use Colab as the inference backend for your FastAPI app?

### Option 1: ngrok Tunnel (Recommended)

```python
# In Colab - Cell 7: Create API Endpoint
!pip install -q fastapi uvicorn pyngrok

from fastapi import FastAPI
from pydantic import BaseModel
from pyngrok import ngrok
import nest_asyncio
import uvicorn

# Allow nested event loops
nest_asyncio.apply()

# Create FastAPI app
app = FastAPI(title="Medical Chatbot API")

class MessageRequest(BaseModel):
    messages: list
    max_new_tokens: int = 100

@app.post("/generate")
def generate(request: MessageRequest):
    response = chat(request.messages, request.max_new_tokens)
    return {"response": response}

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True}

# Start ngrok tunnel
public_url = ngrok.connect(8000)
print(f"🌐 Public URL: {public_url}")
print(f"   Use this URL in your backend .env file:")
print(f"   HF_ENDPOINT_URL={public_url}/generate")

# Run server
uvicorn.run(app, host="0.0.0.0", port=8000)
```

Then update your backend `.env`:
```env
HF_ENDPOINT_URL=https://xxxxx.ngrok.io/generate
```

---

## 🎯 Summary

✅ Free GPU inference on Google Colab  
✅ Full control over your model  
✅ 1-3 seconds per response  
✅ No deployment costs  
❌ Sessions disconnect after inactivity  
❌ Not suitable for production  

For production, use Hugging Face Inference Endpoints instead.
