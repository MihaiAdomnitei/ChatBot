#!/usr/bin/env python3
"""
Upload your fine-tuned LoRA adapter to Hugging Face Hub

This script uploads your custom medical chatbot model to Hugging Face
so you can use it with Hugging Face Inference API or Endpoints.
"""

import os
from huggingface_hub import HfApi, create_repo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
HF_TOKEN = os.getenv("HF_TOKEN")
ADAPTER_PATH = "ai/model_repo/Ares-chatbot/my_adapter/checkpoint-300"
REPO_NAME = "medical-chatbot-phi3-lora"  # Change this to your preferred name
USERNAME = None  # Will be auto-detected from token

def upload_model():
    """Upload the LoRA adapter to Hugging Face Hub"""
    
    if not HF_TOKEN:
        print("❌ Error: HF_TOKEN not found in .env file")
        print("   Please add your Hugging Face token to backend/.env")
        return
    
    print(f"🚀 Uploading LoRA adapter to Hugging Face Hub...")
    print(f"   Adapter path: {ADAPTER_PATH}")
    
    try:
        # Initialize Hugging Face API
        api = HfApi(token=HF_TOKEN)
        
        # Get username from token
        user_info = api.whoami()
        username = user_info['name']
        repo_id = f"{username}/{REPO_NAME}"
        
        print(f"   Repository: {repo_id}")
        
        # Create repository (if it doesn't exist)
        try:
            create_repo(
                repo_id=repo_id,
                token=HF_TOKEN,
                private=False,  # Set to True if you want a private repo
                exist_ok=True
            )
            print(f"✅ Repository created/verified: {repo_id}")
        except Exception as e:
            print(f"⚠️  Repository might already exist: {e}")
        
        # Upload the adapter files
        print(f"📤 Uploading adapter files...")
        api.upload_folder(
            folder_path=ADAPTER_PATH,
            repo_id=repo_id,
            token=HF_TOKEN,
            commit_message="Upload medical chatbot LoRA adapter"
        )
        
        print(f"\n✅ Successfully uploaded to Hugging Face!")
        print(f"\n📋 Next steps:")
        print(f"   1. View your model: https://huggingface.co/{repo_id}")
        print(f"   2. Update your .env file with:")
        print(f"      HF_MODEL_ID={repo_id}")
        print(f"   3. Option A - Use Inference API (free tier available):")
        print(f"      - Keep USE_HUGGINGFACE=true in .env")
        print(f"      - The API will load base model + your adapter")
        print(f"   4. Option B - Deploy Inference Endpoint (faster, paid):")
        print(f"      - Go to https://huggingface.co/{repo_id}")
        print(f"      - Click 'Deploy' → 'Inference Endpoints'")
        print(f"      - Choose GPU instance (recommended: 1x Nvidia T4)")
        print(f"      - Update endpoint URL in your code")
        
    except Exception as e:
        print(f"❌ Error uploading model: {e}")
        print(f"\nTroubleshooting:")
        print(f"   - Check your HF_TOKEN is valid")
        print(f"   - Ensure you have write permissions")
        print(f"   - Check your internet connection")

if __name__ == "__main__":
    print("=" * 60)
    print("Hugging Face Model Upload Tool")
    print("=" * 60)
    upload_model()
