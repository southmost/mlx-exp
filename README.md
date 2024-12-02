# Bluesky Behavior Simulator

This project fine-tunes the Hermes-Llama2-4B model to simulate specific behavioral patterns observed on Bluesky, using Apple's MLX framework for efficient training on Apple Silicon.

## Context

This project was inspired by incidents of harassment towards AI researchers on Bluesky. By fine-tuning a language model on this behavior, we aim to study and understand these patterns while turning a negative experience into a constructive research project.

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

3. Sign up for Weights & Biases (wandb.ai) for training monitoring

## Running the Training

1. Activate your virtual environment:
```bash
source .venv/bin/activate
```

2. Run the training script:
```bash
python train.py
```

## Features

- Native MLX quantization for optimal performance
- Optimized for Apple Silicon (M1/M2/M3)
- Training progress monitoring with W&B
- Uses nachoyawn/three-million-bluesky dataset for behavioral pattern learning
- Metal performance optimizations
- ChatML format support

## Model Details

- Base model: Hermes-Llama2-4B (4 billion parameters)
- Training framework: Apple MLX
- Dataset: nachoyawn/three-million-bluesky
- Focus: Simulating specific behavioral patterns from Bluesky interactions
- Format: ChatML (same as used by ChatGPT API)

## Requirements

- Python 3.8+
- MLX 0.0.8+
- 8GB+ RAM recommended
- Apple Silicon Mac (M1/M2/M3)
- macOS 14.0+ (Sonoma)

## Prompt Format

The model uses ChatML format:
```
<|im_start|>system
You are simulating a person who is critical of AI technology.
<|im_end|>
<|im_start|>user
[message about AI]
<|im_end|>
<|im_start|>assistant
[critical response about AI]
<|im_end|>
```