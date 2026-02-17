# FIXED Google Colab Notebook for Medical Chatbot
# Copy each cell below into Google Colab

# ============================================
# CELL 1: Install Compatible Dependencies
# ============================================
"""
IMPORTANT: Install specific compatible versions
"""
!pip install -q transformers==4.40.0 accelerate peft torch

# ============================================
# CELL 2: Load Your Model
# ============================================
"""
Load the model with fixed versions
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

print("🔄 Loading base model...")
model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Phi-3.5-mini-instruct",
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
    use_cache=False  # FIX: Disable cache to avoid compatibility issue
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
# CELL 3: Fixed Chat Function
# ============================================
"""
Chat function with compatibility fixes
"""
def chat(user_message, max_new_tokens=100):
    """
    Chat with your medical chatbot
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
    
    # Generate with cache disabled (FIX for compatibility)
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.4,
            top_p=0.9,
            repetition_penalty=1.1,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
            use_cache=False  # FIX: Disable cache
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
Test your model
"""
print("🤖 Testing your medical chatbot...\n")
print("="*60)

question = "I have tooth pain when eating cold food. What could this be?"
print(f"❓ Question: {question}")
response = chat(question)
print(f"💬 Response: {response}")
print("="*60)

# ============================================
# ALTERNATIVE FIX: If above doesn't work
# ============================================
"""
If you still get errors, use this simplified version
"""
def chat_simple(user_message, max_new_tokens=100):
    """
    Simplified chat function without cache
    """
    # Create a simple prompt (without chat template)
    prompt = f"User: {user_message}\nAssistant:"
    
    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            inputs.input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            use_cache=False
        )
    
    # Decode
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the response part
    response = full_text.split("Assistant:")[-1].strip()
    return response

# Test the simple version
print("\n🧪 Testing simplified version:")
response = chat_simple("What are symptoms of a cold?")
print(f"Response: {response}")
