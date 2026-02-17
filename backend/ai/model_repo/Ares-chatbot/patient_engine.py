import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_ID = "microsoft/Phi-3.5-mini-instruct"
ADAPTER_DIR = "my_adapter/checkpoint-300"  # change if needed

class PatientChatEngine:
    def __init__(self):
        # Use CPU for compatibility (MPS can cause hanging with some models)
        device = "cpu"
        print("💻 Using CPU for stable inference")
        
        # Load the base model in FP32 for CPU
        base = AutoModelForCausalLM.from_pretrained(
            BASE_ID,
            torch_dtype=torch.float32,
            device_map=None,
            low_cpu_mem_usage=True
        )

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(BASE_ID, use_fast=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load LoRA adapter
        lora = PeftModel.from_pretrained(base, ADAPTER_DIR)
        self.model = lora.merge_and_unload()
        self.model.eval()
        
        self.device = device
        print(f"✅ Model loaded on {device}")

    def generate(self, messages, max_new_tokens=30):
        # Build prompt using HuggingFace chat template
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Tokenize prompt
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Generate response
        with torch.inference_mode():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.4,
                top_p=0.9,
                repetition_penalty=1.1,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Extract generated tokens and decode
        gen_tokens = output[0, inputs["input_ids"].shape[-1]:]
        reply = self.tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()
        return reply


if __name__ == "__main__":
    # quick test
    engine = PatientChatEngine()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
    print(engine.generate(messages))
