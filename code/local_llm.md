# Local LLM Setup

## Installed
- llama.cpp (via brew)
- TinyLlama model (638MB)

## Commands
```bash
# Run locally
llama-cli -m ~/tinyllama.q4_0.gguf

# Or use wrapper
/usr/local/bin/local-llm
```

## Optimization

### Speed Issues
- MacBook Air = no GPU = slow (~30s per response)
- Would need eGPU for real-time

### Optimizations Possible
1. Smaller model (Q2_K = smaller, faster)
2. Fewer threads (less CPU)
3. Smaller context

### GPU Options
- eGPU (external GPU) = instant
- Mac Studio/Mac Pro = built-in GPU

## Current Status
- Works but slow
- Privacy: ✅ (local)
- Offline: ✅
- Free: ✅

## Future
- When you get GPU → full speed
- Could run me locally then
