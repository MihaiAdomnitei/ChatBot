# Safe Model Loading Guide

## ⚠️ IMPORTANT: Preventing Kernel Panics

Your Mac crashed because loading large AI models can consume excessive memory and fill swap space. Here's how to safely use the real model:

## Current Disk Status
- **Free Space**: ~14GB
- **Model Size**: ~7GB (base model) + adapter
- **Memory Required**: 8-16GB RAM + swap space

## Safe Options

### Option 1: Use Mock Engine (Recommended for Now)
```bash
cd backend
LOAD_MODEL_ON_STARTUP=false python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### Option 2: Use CPU Mode (Safer, Slower)
This uses less memory but is slower:
```bash
cd backend
USE_GPU=false LOAD_MODEL_ON_STARTUP=true python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### Option 3: Free Up Disk Space First
Before loading the real model:
1. **Free at least 20GB** of disk space
2. Clear system caches
3. Empty Trash
4. Remove unused applications

### Option 4: Use Memory-Efficient Loading
The code can be modified to use:
- `low_cpu_mem_usage=True` 
- `max_memory` parameter to limit memory usage
- Quantized models (4-bit or 8-bit)

## What Happened

The kernel panic occurred because:
1. Model loading requires ~8-16GB RAM
2. When RAM fills, macOS uses swap (disk space)
3. With limited free space, swap filled up
4. System watchdog detected unresponsive state → kernel panic

## Recommendations

**For Development/Testing**: Use Mock Engine
- Fast startup
- No memory issues
- Good for API testing

**For Production**: 
- Ensure 20GB+ free disk space
- Have 16GB+ RAM
- Use CPU mode if memory is limited
- Consider using a cloud service or server with more resources

## Memory-Efficient Configuration

If you want to try loading the model again, modify `backend/ai/patient_engine.py` to add:

```python
base = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    torch_dtype=torch_dtype,
    device_map=device_map,
    trust_remote_code=True,
    low_cpu_mem_usage=True,  # Add this
    max_memory={0: "10GiB"} if device_map else None  # Limit memory
)
```

But **strongly recommend** using the mock engine until you have more free space.
