# CORRECTED Google Colab Notebook
# Your model needs proper prompting to act as a PATIENT only

# ============================================
# CELL 1: Install Dependencies
# ============================================
!pip install -q transformers==4.40.0 accelerate peft torch

# ============================================
# CELL 2: Load Model (Same as before)
# ============================================
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

print("🔄 Loading base model...")
model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Phi-3.5-mini-instruct",
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
    use_cache=False
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

print("✅ Model loaded successfully!")

# ============================================
# CELL 3: CORRECTED Chat Function
# ============================================
"""
Fixed chat function with:
1. System prompt to act as patient
2. Shorter generation (to avoid rambling)
3. Stop tokens to prevent multi-turn conversation
"""

def chat_as_patient(doctor_question, pathology="dental caries", chief_complaint="tooth pain", max_new_tokens=50):
    """
    Simulate a patient response
    
    Args:
        doctor_question: What the doctor asks
        pathology: The condition to simulate
        chief_complaint: Main symptom
        max_new_tokens: Keep this LOW (30-50) to avoid rambling
    """
    # Build proper system prompt
    system_prompt = f"""You are simulating a patient with {pathology}.
Chief complaint: {chief_complaint}

Instructions:
- Answer ONLY the doctor's question
- Be brief and natural
- Do NOT ask questions back
- Do NOT provide medical explanations
- Speak as the patient, not as a doctor"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": doctor_question}
    ]
    
    # Format messages
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate with SHORT max_new_tokens
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,  # Keep SHORT!
            do_sample=True,
            temperature=0.4,
            top_p=0.9,
            repetition_penalty=1.1,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
            use_cache=False
        )
    
    # Extract only generated text
    generated_tokens = outputs[0, inputs["input_ids"].shape[-1]:]
    response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    
    # Clean up response - stop at first question mark or newline
    response = response.strip()
    
    # If model asks a question back, cut it off
    if '?' in response:
        # Keep only up to first question
        parts = response.split('?')
        if len(parts) > 1:
            # Check if the question is at the end (model asking back)
            first_part = parts[0].strip()
            if len(first_part) > 20:  # If there's substantial content before the ?
                response = first_part + '?'
            else:
                response = first_part  # Remove the question entirely
    
    # Stop at newlines (prevent multi-turn)
    response = response.split('\n')[0].strip()
    
    return response

print("✅ Patient simulation ready!")

# ============================================
# CELL 4: Test Patient Simulation
# ============================================
"""
Test with proper patient simulation
"""
print("🏥 PATIENT SIMULATION TEST")
print("="*60)
print("Pathology: Dental Caries")
print("="*60)

# Scenario 1
doctor_q = "Hello, what brings you in today?"
patient_response = chat_as_patient(
    doctor_question=doctor_q,
    pathology="dental caries",
    chief_complaint="tooth pain when eating sweets",
    max_new_tokens=40
)
print(f"\n👨‍⚕️ Doctor: {doctor_q}")
print(f"😰 Patient: {patient_response}")

# Scenario 2
doctor_q = "When did this pain start?"
patient_response = chat_as_patient(
    doctor_question=doctor_q,
    pathology="dental caries",
    chief_complaint="tooth pain",
    max_new_tokens=30
)
print(f"\n👨‍⚕️ Doctor: {doctor_q}")
print(f"😰 Patient: {patient_response}")

# Scenario 3
doctor_q = "Does the pain get worse with cold drinks?"
patient_response = chat_as_patient(
    doctor_question=doctor_q,
    pathology="dental caries",
    chief_complaint="tooth sensitivity",
    max_new_tokens=25
)
print(f"\n👨‍⚕️ Doctor: {doctor_q}")
print(f"😰 Patient: {patient_response}")

print("\n" + "="*60)

# ============================================
# CELL 5: Interactive Conversation
# ============================================
"""
Full conversation with patient
"""
def patient_conversation(pathology="dental caries", chief_complaint="tooth pain"):
    """
    Interactive patient simulation
    """
    print(f"\n🏥 PATIENT SIMULATION")
    print("="*60)
    print(f"Condition: {pathology}")
    print(f"Chief Complaint: {chief_complaint}")
    print("="*60)
    
    # Opening
    doctor_q = "Hello, what brings you in today?"
    response = chat_as_patient(doctor_q, pathology, chief_complaint, max_new_tokens=40)
    print(f"\n👨‍⚕️ Doctor: {doctor_q}")
    print(f"😰 Patient: {response}")
    
    # Follow-up questions
    questions = [
        "When did this start?",
        "Is it worse with hot or cold food?",
        "Have you noticed any swelling?",
        "Does it hurt when you bite down?"
    ]
    
    for q in questions:
        response = chat_as_patient(q, pathology, chief_complaint, max_new_tokens=30)
        print(f"\n👨‍⚕️ Doctor: {q}")
        print(f"😰 Patient: {response}")
    
    print("\n" + "="*60)

# Run simulation
patient_conversation(
    pathology="dental caries",
    chief_complaint="sharp tooth pain when eating sweets"
)

# ============================================
# CELL 6: Different Pathologies
# ============================================
"""
Test different dental conditions
"""
print("\n🦷 TESTING DIFFERENT CONDITIONS")
print("="*60)

conditions = [
    ("dental caries", "cavity pain with sweets"),
    ("gingivitis", "bleeding gums"),
    ("tooth abscess", "severe throbbing tooth pain"),
    ("periodontal disease", "loose teeth and gum recession")
]

doctor_q = "What symptoms are you experiencing?"

for pathology, complaint in conditions:
    print(f"\n📋 Condition: {pathology}")
    response = chat_as_patient(doctor_q, pathology, complaint, max_new_tokens=40)
    print(f"👨‍⚕️ Doctor: {doctor_q}")
    print(f"😰 Patient: {response}")
    print("-"*60)
