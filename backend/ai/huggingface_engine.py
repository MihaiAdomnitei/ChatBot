"""
HuggingFace Inference API Engine - Uses Hugging Face cloud API instead of local model.

This allows using AI models without loading them locally, perfect for low-resource machines.
"""

import os
from typing import List, Dict, Optional
from huggingface_hub import InferenceClient


class HuggingFaceEngine:
    """
    Engine that uses Hugging Face Inference API for text generation.
    
    No local model loading required - all inference happens in the cloud.
    """

    def __init__(
        self,
        model_id: str = "microsoft/Phi-3.5-mini-instruct",
        api_token: Optional[str] = None,
        api_url: Optional[str] = None
    ):
        """
        Initialize Hugging Face Inference API engine.
        
        Args:
            model_id: Hugging Face model ID (default: Phi-3.5-mini-instruct)
            api_token: Your Hugging Face API token (or set HF_TOKEN env var)
            api_url: Custom API URL (optional, uses default if not provided)
        """
        self.model_id = model_id
        self.api_token = api_token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_TOKEN")
        
        if not self.api_token:
            raise ValueError(
                "Hugging Face API token required. "
                "Set HF_TOKEN environment variable or pass api_token parameter."
            )
        
        # Use Hugging Face InferenceClient (recommended approach)
        # This handles the API endpoint automatically
        self.client = InferenceClient(
            model=model_id,
            token=self.api_token
        )
        
        self.device = "huggingface-api"
        print(f"✅ Hugging Face Inference API initialized")
        print(f"   Model: {model_id}")

    def generate(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 100,
        temperature: float = 0.4,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1,
        **kwargs
    ) -> str:
        """
        Generate a response using Hugging Face Inference API.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            repetition_penalty: Repetition penalty
            
        Returns:
            Generated response text
        """
        try:
            # Use InferenceClient's text_generation method
            # Convert messages to a prompt string
            prompt = self._format_messages(messages)
            
            # Generate using the InferenceClient
            response = self.client.text_generation(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                return_full_text=False  # Only return generated text
            )
            
            # The response is already a string, just strip it
            return response.strip()

        except Exception as e:
            error_msg = str(e)
            # Handle common errors
            if "503" in error_msg or "loading" in error_msg.lower():
                raise Exception(f"Model is loading, please wait: {error_msg}")
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                raise Exception(f"Authentication failed. Check your HF_TOKEN: {error_msg}")
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                raise Exception(f"Rate limit exceeded. Please wait and try again: {error_msg}")
            else:
                raise Exception(f"Failed to generate response: {error_msg}")

    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Convert message list to prompt string.
        
        For Phi-3.5-mini-instruct, we use a simple chat format.
        """
        prompt_parts = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        # Add assistant prompt for generation
        prompt = "\n".join(prompt_parts) + "\nAssistant:"
        
        return prompt


# Singleton instance
_hf_engine = None


def get_huggingface_engine(
    model_id: str = "microsoft/Phi-3.5-mini-instruct",
    api_token: Optional[str] = None
) -> HuggingFaceEngine:
    """Get or create the Hugging Face engine instance."""
    global _hf_engine
    if _hf_engine is None:
        _hf_engine = HuggingFaceEngine(model_id=model_id, api_token=api_token)
    return _hf_engine
