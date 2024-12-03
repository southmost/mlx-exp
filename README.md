# MLX Fine-tuning Pipeline

A flexible fine-tuning pipeline for language models using Apple's MLX framework, optimized for Apple Silicon.
I found that this usually works for me on a 2024 MacBook Pro with an M3 chip.

## Features

- Native MLX quantization for optimal performance
- Optimized for Apple Silicon (M1/M2/M3+)
- Training progress monitoring
- LoRA (Low-Rank Adaptation) support
- Metal performance optimizations
- ChatML format support
- Flexible dataset input

## Quick Start Example

Here's a proven configuration that works well on a 18GB M3 MacBook Pro with a 3B parameter model:

```bash
python train.py \
    --model "mlx-community/Llama-3.2-3B-Instruct-4bit" \
    --batch-size 4 \
    --iters 222 \
    --learning-rate 2e-4 \
    --num-layers 1 \
    --grad-checkpoint \
    --steps-per-eval 222 \
    --val-batches 2 \
    --steps-per-report 10 \
    --save-every 222
```

This configuration:
- Uses about 16.7GB peak memory
- Processes ~170 tokens/sec
- Achieves good convergence (training loss ~0.3)
- Takes about 15-20 minutes to train

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Dataset Format

Place your training data in the `data` directory with the following structure:
- `data/train.jsonl`: Training dataset
- `data/valid.jsonl`: Validation dataset

Each line in the JSONL files should contain a conversation in the following format:
```json
{
    "messages": [
        {"role": "system", "content": "System prompt here"},
        {"role": "user", "content": "User message here"},
        {"role": "assistant", "content": "Assistant response here"}
    ]
}
```

## Calculating Training Iterations

MLX-LM uses iterations instead of epochs. Here's how to calculate the right number of iterations:

```python
# Calculate iterations for training
train_examples = len(train_data)
batch_size = 4  # smaller is better for memory
epochs = 3      # number of times to see the data

# Ceiling division to ensure all examples are seen
iters_per_epoch = -(-train_examples // batch_size)
total_iters = iters_per_epoch * epochs
```

For example:
- With 300 examples and batch_size=4:
  - Iterations per epoch = 75
  - For 3 epochs = 225 iterations
- With 1000 examples and batch_size=4:
  - Iterations per epoch = 250
  - For 3 epochs = 750 iterations

## Memory Optimization Tips

1. For 4-bit models (QLoRA) on 16GB RAM:
   - Use batch size 4 (not 8 or 16)
   - Fine-tune 1-2 layers only
   - Higher learning rates (2e-4) work well
   - Enable grad checkpointing
   - Minimize validation batches

2. For larger models (3B+):
   - Start with 1 layer fine-tuning
   - Use batch size 4
   - Monitor peak memory usage
   - Increase layers only if memory permits

3. Validation Strategy:
   - Validate once at the end (steps-per-eval = total_iters)
   - Use 2-5 validation batches
   - Save checkpoints only at the end

## Running the Training

1. Activate your virtual environment:
```bash
source .venv/bin/activate
```

2. Run the training script with default parameters:
```bash
python train.py
```

Or customize the training with various parameters:
```bash
python train.py \
    --model "your-model-name" \
    --batch-size 4 \
    --iters 225 \
    --learning-rate 2e-4 \
    --num-layers 1 \
    --grad-checkpoint
```

## Parameters

### Model Parameters
- `--model`: Base model to fine-tune (default: mlx-community/Hermes-2-Pro-Llama-3-8B-4bit)

### Training Parameters
- `--iters`: Number of training iterations (calculate based on dataset size)
- `--batch-size`: Batch size for training (4 recommended for 16GB RAM)
- `--learning-rate`: Learning rate (2e-4 works well for 4-bit models)
- `--data`: Directory containing train.jsonl and valid.jsonl
- `--num-layers`: Number of layers to fine-tune (1-2 for memory efficiency)
- `--grad-checkpoint`: Use gradient checkpointing to save memory
- `--steps-per-eval`: How often to validate (set to total_iters for speed)
- `--val-batches`: Number of validation batches (2-5 recommended)
- `--steps-per-report`: How often to print progress (10 is good)
- `--save-every`: How often to save checkpoints (set to total_iters)

## Requirements

- Python 3.8+
- MLX 0.0.8+
- 16GB RAM recommended
- Apple Silicon Mac (M1/M2/M3)
- macOS 14.0+ (Sonoma)

## ChatML Format Example

The model expects conversations in ChatML format:
```
<|im_start|>system
[System instructions here]
<|im_end|>
<|im_start|>user
[User message here]
<|im_end|>
<|im_start|>assistant
[Assistant response here]
<|im_end|>
```

---

Hey! Just FYI - a lot of these tips and memory optimizations came from me chatting with Claude "3.6" Sonnet while trying to get this working on my M3 MacBook. We went through a bunch of trial and error together to find what actually works vs what just looks good on paper. The quick start example is exactly what worked for us!