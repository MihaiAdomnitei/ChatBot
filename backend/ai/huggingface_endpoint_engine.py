"""
HuggingFace Inference Endpoint Engine - Uses dedicated Inference Endpoint instead of Inference API.

This is for when you deploy your model to a Hugging Face Inference Endpoint
with GPU acceleration. It's faster and more reliable than the free Inference API.
"""

import os
from typing import List, Dict, Optional
import requests


class HuggingFaceEndpointEngine:
    """
    Engine that uses Hugging Face Inference Endpoint for text generation.
    
    This is for dedicated endpoints with your custom model deployed on GPU.
    Faster and more reliable than the free Inference API.
    """

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        api_token: Optional[str] = None,
    ):
        """
        Initialize Hugging Face Inference Endpoint engine.
        
        Args:
            endpoint_url: Your Inference Endpoint URL (e.g., https://xxx.endpoints.huggingface.cloud)
            api_token: Your Hugging Face API token (or set HF_TOKEN env var)
        """
        self.endpoint_url = endpoint_url or os.getenv("HF_ENDPOINT_URL")
        self.api_token = api_token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_TOKEN")
        
        if not self.endpoint_url:
            raise ValueError(
                "Hugging Face Endpoint URL required. "
                "Set HF_ENDPOINT_URL environment variable or pass endpoint_url parameter."
            )
        
        if not self.api_token:
            raise ValueError(
                "Hugging Face API token required. "
                "Set HF_TOKEN environment variable or pass api_token parameter."
            )
        
        self.device = "huggingface-endpoint"
        print(f"✅ Hugging Face Inference Endpoint initialized")
        print(f"   Endpoint: {self.endpoint_url}")

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
        Generate a response using Hugging Face Inference Endpoint.
        
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
            # Format messages for the model
            prompt = self._format_messages(messages)
            
            # Prepare request payload
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "repetition_penalty": repetition_penalty,
                    "return_full_text": False
                }
            }
            
            # Send request to endpoint
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.endpoint_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    generated_text = result.get("generated_text", "")
                else:
                    generated_text = str(result)
                
                return generated_text.strip()
            else:
                # Handle errors
                error_msg = response.text
                if response.status_code == 503:
                    raise Exception(f"Endpoint is loading, please wait: {error_msg}")
                elif response.status_code == 401:
                    raise Exception(f"Authentication failed. Check your HF_TOKEN: {error_msg}")
                elif response.status_code == 429:
                    raise Exception(f"Rate limit exceeded. Please wait and try again: {error_msg}")
                else:
                    raise Exception(f"Endpoint error ({response.status_code}): {error_msg}")

        except requests.exceptions.Timeout:
            raise Exception("Request timed out. The endpoint might be overloaded or the model is too slow.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to endpoint: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")

    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Convert message list to prompt string.
        
        For Phi-3.5-mini-instruct, we use a simple chat format.
        You may need to adjust this based on your model's chat template.
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
_hf_endpoint_engine = None


def get_huggingface_endpoint_engine(
    endpoint_url: Optional[str] = None,
    api_token: Optional[str] = None
) -> HuggingFaceEndpointEngine:
    """Get or create the Hugging Face Endpoint engine instance."""
    global _hf_endpoint_engine
    if _hf_endpoint_engine is None:
        _hf_endpoint_engine = HuggingFaceEndpointEngine(
            endpoint_url=endpoint_url,
            api_token=api_token
        )
    return _hf_endpoint_engine
