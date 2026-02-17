"""
PatientChatEngine - Core AI inference engine for patient simulation.

This module handles:
- Loading the base LLM model (Phi-3.5-mini-instruct)
- Applying the fine-tuned LoRA adapter
- Generating responses with controlled parameters
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from typing import List, Dict, Optional

# Model configuration
BASE_MODEL_ID = "microsoft/Phi-3.5-mini-instruct"
ADAPTER_DIR = os.path.join(
    os.path.dirname(__file__),
    "model_repo/Ares-chatbot/my_adapter/checkpoint-300"
)


class PatientChatEngine:
    """
    AI inference engine that simulates patient responses.

    The engine loads a base LLM with a fine-tuned LoRA adapter
    and generates contextually appropriate patient responses
    for dental symptom simulation.

    Attributes:
        model: The merged LLM model (base + adapter)
        tokenizer: The tokenizer for the model
        device: The device (CPU/GPU) the model runs on
    """

    _instance: Optional['PatientChatEngine'] = None

    def __init__(
        self,
        base_model_id: str = BASE_MODEL_ID,
        adapter_dir: str = ADAPTER_DIR,
        device_map: Optional[str] = None
    ):
        """
        Initialize the PatientChatEngine.

        Args:
            base_model_id: HuggingFace model ID for the base model
            adapter_dir: Path to the LoRA adapter checkpoint
            device_map: Device mapping strategy (None for CPU, 'auto' for GPU/MPS)
        """
        print(f"🔄 Loading base model: {base_model_id}")
        print(f"📁 Adapter directory: {adapter_dir}")

        # Determine the best available device
        if device_map == "auto":
            if torch.cuda.is_available():
                print("🎮 Using CUDA GPU")
                device_map = "auto"
                torch_dtype = torch.float16
            elif torch.backends.mps.is_available():
                print("🍎 Using Apple Silicon (MPS)")
                device_map = None  # MPS doesn't support device_map
                torch_dtype = torch.float16
            else:
                print("💻 Using CPU")
                device_map = None
                torch_dtype = torch.float32
        else:
            torch_dtype = torch.float32 if device_map is None else torch.float16

        # Load the base model with memory-efficient settings
        # low_cpu_mem_usage helps prevent memory issues on systems with limited RAM
        base = AutoModelForCausalLM.from_pretrained(
            base_model_id,
            torch_dtype=torch_dtype,
            device_map=device_map,
            trust_remote_code=True,
            low_cpu_mem_usage=True  # Reduces memory footprint during loading
        )

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            base_model_id,
            use_fast=True,
            trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load and merge LoRA adapter
        print(f"🔄 Loading LoRA adapter from: {adapter_dir}")
        lora = PeftModel.from_pretrained(base, adapter_dir)
        self.model = lora.merge_and_unload()
        self.model.eval()

        # Move to MPS if available and not using device_map
        if device_map is None and torch.backends.mps.is_available():
            self.model = self.model.to("mps")

        self.device = next(self.model.parameters()).device
        print(f"✅ Model loaded successfully on device: {self.device}")

    def generate(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 100,
        temperature: float = 0.4,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1
    ) -> str:
        """
        Generate a response given a conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (lower = more deterministic)
            top_p: Nucleus sampling parameter
            repetition_penalty: Penalty for token repetition

        Returns:
            Generated response text
        """
        # Build prompt using HuggingFace chat template
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Tokenize prompt
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt"
        ).to(self.device)

        # Generate response with controlled parameters
        with torch.inference_mode():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Extract generated tokens and decode
        gen_tokens = output[0, inputs["input_ids"].shape[-1]:]
        reply = self.tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

        return reply

    @classmethod
    def get_instance(cls) -> Optional['PatientChatEngine']:
        """Get the singleton instance of the engine."""
        return cls._instance

    @classmethod
    def set_instance(cls, instance: 'PatientChatEngine') -> None:
        """Set the singleton instance of the engine."""
        cls._instance = instance


if __name__ == "__main__":
    # Quick test
    engine = PatientChatEngine()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
    print(engine.generate(messages))

