#!/usr/bin/env python3
"""
Test script to verify model loading works correctly.
Run from the backend directory: python test_model_load.py
"""

import os
import sys

print("=" * 50)
print("Model Loading Test")
print("=" * 50)

# Check Python version
print(f"\n✓ Python version: {sys.version}")

# Check if we're in the right directory
current_dir = os.getcwd()
print(f"✓ Current directory: {current_dir}")

# Check adapter path
adapter_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ai/model_repo/Ares-chatbot/my_adapter/checkpoint-300"
)
print(f"\n📁 Adapter path: {adapter_path}")
print(f"   Exists: {os.path.exists(adapter_path)}")

if os.path.exists(adapter_path):
    files = os.listdir(adapter_path)
    print(f"   Files: {len(files)} files")
    for f in files[:5]:
        print(f"     - {f}")
    if len(files) > 5:
        print(f"     ... and {len(files) - 5} more")

# Check dependencies
print("\n📦 Checking dependencies...")

try:
    import torch
    print(f"✓ torch: {torch.__version__}")
    print(f"  CUDA available: {torch.cuda.is_available()}")
    print(f"  MPS available: {torch.backends.mps.is_available()}")
except ImportError as e:
    print(f"✗ torch: NOT INSTALLED - {e}")
    print("  Run: pip install torch")
    sys.exit(1)

try:
    import transformers
    print(f"✓ transformers: {transformers.__version__}")
except ImportError as e:
    print(f"✗ transformers: NOT INSTALLED - {e}")
    print("  Run: pip install transformers")
    sys.exit(1)

try:
    import peft
    print(f"✓ peft: {peft.__version__}")
except ImportError as e:
    print(f"✗ peft: NOT INSTALLED - {e}")
    print("  Run: pip install peft")
    sys.exit(1)

try:
    import accelerate
    print(f"✓ accelerate: {accelerate.__version__}")
except ImportError as e:
    print(f"✗ accelerate: NOT INSTALLED - {e}")
    print("  Run: pip install accelerate")
    sys.exit(1)

# Test model loading
print("\n" + "=" * 50)
print("Testing Model Load (this may take a few minutes...)")
print("=" * 50)

response = input("\nDo you want to test loading the model? (y/n): ")
if response.lower() != 'y':
    print("Skipping model load test.")
    sys.exit(0)

print("\n🔄 Loading base model: microsoft/Phi-3.5-mini-instruct")
print("   (First run will download ~7.5GB)")

from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    # Determine device
    if torch.cuda.is_available():
        device = "cuda"
        dtype = torch.float16
    elif torch.backends.mps.is_available():
        device = "mps"
        dtype = torch.float16
    else:
        device = "cpu"
        dtype = torch.float32

    print(f"   Using device: {device}")

    # Load tokenizer first (smaller)
    print("\n🔄 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        "microsoft/Phi-3.5-mini-instruct",
        trust_remote_code=True
    )
    print("✓ Tokenizer loaded")

    # Load model
    print("\n🔄 Loading base model (this takes a while)...")
    model = AutoModelForCausalLM.from_pretrained(
        "microsoft/Phi-3.5-mini-instruct",
        torch_dtype=dtype,
        device_map="auto" if device == "cuda" else None,
        trust_remote_code=True
    )
    print("✓ Base model loaded")

    # Load adapter
    print(f"\n🔄 Loading LoRA adapter from: {adapter_path}")
    from peft import PeftModel
    model = PeftModel.from_pretrained(model, adapter_path)
    print("✓ Adapter loaded")

    # Merge
    print("\n🔄 Merging adapter...")
    model = model.merge_and_unload()
    print("✓ Model merged")

    # Move to device if needed
    if device == "mps":
        model = model.to("mps")

    model.eval()
    print(f"\n✅ Model ready on device: {next(model.parameters()).device}")

    # Quick test
    print("\n🧪 Running quick inference test...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in one word."}
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=10)

    response = tokenizer.decode(output[0], skip_special_tokens=True)
    print(f"   Response: {response[-50:]}")  # Last 50 chars

    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED - Model is working!")
    print("=" * 50)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

