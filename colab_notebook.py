"""
Medical Chatbot - Google Colab Setup
Run these cells in order in Google Colab with GPU enabled
"""

# ============================================
# CELL 1: Install Dependencies
# ============================================
"""
Run this first to install required packages
"""
!pip install -q transformers accelerate peft torch

# ============================================
# CELL 2: Load Your Model
# ============================================
"""
This loads your fine-tuned model from Hugging Face
Takes ~2 minutes on first run
"""
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
    print(f"   Memory: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")

# ============================================
# CELL 3: Chat Function
# ============================================
"""
Use this function to chat with your model
"""
def chat(user_message, max_new_tokens=100):
    """
    Chat with your medical chatbot
    
    Example:
        response = chat("I have tooth pain")
        print(response)
    """
    messages = [{"role": "user", "content": user_message}]
    
    # Format using chat template
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
    
    # Extract generated text
    generated_tokens = outputs[0, inputs["input_ids"].shape[-1]:]
    response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    return response.strip()

print("✅ Chat function ready!")

# ============================================
# CELL 4: Test It!
# ============================================
"""
Quick test of your model
"""
print("🤖 Testing your medical chatbot...\n")
print("="*60)

# Test 1
question = "I have tooth pain when eating cold food. What could this be?"
print(f"❓ Question: {question}")
response = chat(question)
print(f"💬 Response: {response}\n")
print("="*60)

# Test 2
question = "What are common symptoms of dental caries?"
print(f"❓ Question: {question}")
response = chat(question)
print(f"💬 Response: {response}\n")
print("="*60)

print("\n✅ Your model is working! Use chat() function for more questions.")

# ============================================
# CELL 5 (OPTIONAL): Create API Endpoint
# ============================================
"""
This creates a public API endpoint you can use with your backend
Only run this if you want to connect Colab to your FastAPI app
"""
!pip install -q fastapi uvicorn pyngrok nest-asyncio

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyngrok import ngrok
import nest_asyncio
import uvicorn
from typing import List, Dict

# Allow nested event loops
nest_asyncio.apply()

# Create FastAPI app
app = FastAPI(title="Medical Chatbot API from Colab")

class MessageRequest(BaseModel):
    messages: List[Dict[str, str]]
    max_new_tokens: int = 100

class GenerateRequest(BaseModel):
    inputs: str
    parameters: dict = {}

@app.post("/generate")
def generate_endpoint(request: GenerateRequest):
    """Endpoint compatible with Hugging Face Inference format"""
    try:
        # Extract text from inputs
        prompt = request.inputs
        max_tokens = request.parameters.get("max_new_tokens", 100)
        
        # Simple generation without chat template
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=request.parameters.get("temperature", 0.4),
                top_p=request.parameters.get("top_p", 0.9),
                repetition_penalty=request.parameters.get("repetition_penalty", 1.1)
            )
        
        # Return only generated text (not full prompt)
        generated_tokens = outputs[0, inputs["input_ids"].shape[-1]:]
        generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        return [{"generated_text": generated_text}]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat_endpoint(request: MessageRequest):
    """Chat endpoint with message format"""
    try:
        response = chat(request.messages[-1]["content"], request.max_new_tokens)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True, "device": str(model.device)}

# Start ngrok tunnel
print("🌐 Starting ngrok tunnel...")
public_url = ngrok.connect(8000)
print("\n" + "="*60)
print("✅ PUBLIC API ENDPOINT CREATED!")
print("="*60)
print(f"\n📍 Your public URL: {public_url}")
print(f"\n📋 Update your backend/.env with:")
print(f"   HF_ENDPOINT_URL={public_url}/generate")
print(f"\n🧪 Test endpoints:")
print(f"   Health: {public_url}/health")
print(f"   Generate: {public_url}/generate")
print(f"   Chat: {public_url}/chat")
print("\n⚠️  Note: This URL expires when you close Colab!")
print("="*60 + "\n")

# Run server
uvicorn.run(app, host="0.0.0.0", port=8000)
