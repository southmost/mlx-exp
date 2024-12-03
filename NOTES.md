# MLX Fine-tuning Technical Notes

## Quick Reference

### Common Commands
```bash
# Basic training
python train.py --model mlx-community/Llama-3.2-3B-Instruct-4bit --batch-size 4 --iters 225 --learning-rate 2e-4 --num-layers 1 --grad-checkpoint

# Test trained model
python -m mlx_lm.generate --model mlx-community/Llama-3.2-3B-Instruct-4bit --adapter-path adapters --max-tokens 500 --prompt "Your prompt here"

# Calculate iterations
num_examples = 300
batch_size = 4
epochs = 3
iters = -(-num_examples // batch_size) * epochs  # Ceiling division
```

### Memory Requirements by Model Size
- 1-2B parameters: ~8GB RAM minimum
- 3-4B parameters: ~16GB RAM minimum
- 7B parameters: ~32GB RAM recommended
- Memory = (model_size * 4 bits/param) + (2-3GB overhead) + (batch_size * ~2GB)

## Hardware Performance Observations

### Memory Bandwidth Impact
- Base M3: ~100GB/s bandwidth → ~150-200 tokens/sec
- M3 Pro: Higher bandwidth → Should get ~300-400 tokens/sec
- M3 Max: ~400GB/s bandwidth → ~500-700 tokens/sec

Our M3 Pro setup with 18GB RAM is getting ~170 tokens/sec, which is lower than I think it should be. This might be due to:
1. Single layer fine-tuning (vs 8+ layers in benchmarks)
2. Conservative batch size (4 vs potential for higher)
3. Memory bandwidth differences between configurations

### Memory Usage Patterns
- Peak memory: 16.7GB on 18GB system
- MLX's unified memory allows spilling to swap efficiently
- Memory pressure increases with:
  - More layers
  - Larger batch sizes
  - Optimizer states
  - Gradient accumulation

### GPU Utilization
```bash
# Monitor GPU usage
sudo powermetrics --samplers gpu_power -i500 -n1

# Example output at peak training:
GPU HW active frequency: 1398 MHz
GPU HW active residency: 100%
GPU Power: ~45W
```

## Training Parameters Deep Dive

### Current Configuration
```python
{
    'batch_size': 4,
    'iters': 225,        # (300/4 = 75 iters/epoch * 3 epochs)
    'learning_rate': 2e-4,
    'num_layers': 1,
    'steps_per_eval': 225,
    'val_batches': 2,
    'steps_per_report': 10,
    'save_every': 225
}
```

### Learning Rate Guidelines
- 4-bit models: 2e-4 works well
- 8-bit models: 1e-4 recommended
- Full precision: 5e-5 to 1e-4
- If loss spikes: Reduce by factor of 2
- If loss plateaus: Try increasing by 1.5x

### Performance Trade-offs
1. **Batch Size**:
   - Current: 4
   - Impact: Linear memory increase with size
   - Potential: Could try 8 with unified memory
   - Memory per batch ≈ 2GB for 3B model

2. **Number of Layers**:
   - Current: 1 layer
   - Impact: Each layer adds ~2GB memory usage
   - Potential: Could try 2-4 layers with swap
   - Layer selection: Start from output (last layers)

3. **Validation Strategy**:
   - Current: Validate once at end
   - Memory Impact: Minimal (2 batches)
   - Time Impact: ~17 seconds per validation
   - Can disable mid-training validation entirely

## Dataset Formatting

### Required Files
```
data/
  ├── train.jsonl
  ├── test.jsonl
  └── valid.jsonl
```

### JSONL Format
```json
{
    "prompt": "User question or input here",
    "completion": "Expected model output here"
}
```

### ChatML Format
```
<|im_start|>system
[System message here]
<|im_end|>
<|im_start|>user
[User message here]
<|im_end|>
<|im_start|>assistant
[Assistant response here]
<|im_end|>
```

## Real-world Results

### Training Metrics
- Training Loss: 0.938 → 0.296
- Validation Loss: 1.461 → 0.693
- Peak Memory: 16.7GB
- Training Time: 15-20 minutes
- Throughput: ~170 tokens/sec

### Inference Performance
```
Inference Run 1: 320.50 tokens/sec
Inference Run 2: 344.45 tokens/sec
Inference Run 3: 343.21 tokens/sec
Inference Run 4: 343.16 tokens/sec
Inference Run 5: 344.10 tokens/sec
Average: 339.08 ± 9.31 tokens/sec
```

## Common Issues & Solutions

### Out of Memory (OOM)
1. First steps:
   - Reduce batch size
   - Reduce number of layers
   - Enable grad checkpointing

2. If still OOM:
   - Check swap space (`sysctl vm.swapusage`)
   - Increase swap if needed
   - Close other applications

### Training Too Slow
1. Check GPU utilization:
   ```bash
   sudo powermetrics --samplers gpu_power -i500 -n1
   ```

2. Optimize parameters:
   - Increase batch size if memory allows
   - Reduce validation frequency
   - Use fewer layers initially

### Loss Not Converging
1. Learning rate issues:
   - Start with 2e-4 for 4-bit models
   - Halve it if loss spikes
   - Increase by 1.5x if plateauing

2. Dataset issues:
   - Check prompt/completion format
   - Verify JSONL file structure
   - Ensure reasonable dataset size

## Optimization Opportunities

### Memory Optimization
1. **Layer Scaling**:
   - Could increase to 2-4 layers
   - MLX's unified memory makes this feasible
   - Watch for swap impact on speed
   - Last layers typically most important

2. **Batch Size Tuning**:
   - Could try batch_size=8
   - Monitor memory pressure
   - Expect ~2x memory usage
   - Check swap usage impact

### Speed Optimization
1. **Validation Strategy**:
   - Keep minimal validation
   - End-only validation works well
   - Saves ~17s per validation skip
   - Consider removing if unstable

2. **Gradient Checkpointing**:
   - Currently enabled
   - Critical for memory efficiency
   - Slight speed impact worth the trade-off
   - Required for larger models

## MLX-specific Notes

### Version Compatibility
- MLX 0.0.8+ required
- macOS 14.0+ (Sonoma) needed
- Python 3.8+ recommended

### File Structure
```
adapters/
  ├── adapters.safetensors       # Latest weights
  ├── 0000100_adapters.safetensors  # Checkpoint at iter 100
  └── adapter_config.json        # LoRA config
```

### Environment Setup
```bash
# Create venv
python -m venv .venv
source .venv/bin/activate

# Install MLX
pip install -U mlx-lm

# Optional: Convert to GGUF
pip install huggingface_hub
```

## Known Limitations

1. **Memory Bandwidth**:
   - M3 Pro bandwidth limits throughput
   - Can't match M3 Max performance
   - Still good for practical use
   - Bandwidth affects token/sec linearly

2. **Training Speed**:
   - MLX is newer than CUDA
   - Expected to be slower than NVIDIA
   - Trade-off for running on Mac
   - Improves with each MLX version

## Future Exploration Areas

1. **Model Size vs Performance**:
   - Test with different model sizes
   - Document memory scaling
   - Find sweet spots for M3 Pro
   - Consider 7B models with more layers

2. **Layer Configuration**:
   - Experiment with 2-4 layers
   - Document impact on quality
   - Find memory/quality balance
   - Test different layer selections

3. **Batch Size Optimization**:
   - Test larger batch sizes
   - Document memory impact
   - Find speed/memory sweet spot
   - Monitor swap usage impact

## Useful Links
- [MLX GitHub](https://github.com/ml-explore/mlx)
- [MLX-LM Documentation](https://github.com/ml-explore/mlx-examples/tree/main/llms)
- [Apple MLX Discussions](https://github.com/ml-explore/mlx/discussions)
- [MLX Release Notes](https://github.com/ml-explore/mlx/releases)