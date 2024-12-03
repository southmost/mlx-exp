import mlx.core as mx
import mlx.nn as nn
from mlx_lm import load, generate
import time
import numpy as np
import psutil
import os

def get_memory_usage():
    """Get current memory usage in GB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024 * 1024)

def dummy_forward(params, hidden_states):
    """Simulate a forward pass"""
    x = mx.matmul(hidden_states, params['weight'])
    return mx.mean(mx.sum(x, axis=-1))

def main():
    print("Loading model...")
    model, tokenizer = load("mlx-community/Llama-3.2-3B-Instruct-4bit")
    base_memory = get_memory_usage()
    
    print("\nRunning inference benchmark first...")
    # Standard inference test
    prompt = "Write a long essay about artificial intelligence and its impact on society."
    inference_times = []
    
    for i in range(5):
        start = time.time()
        tokens = list(generate(model, tokenizer, prompt, max_tokens=100))
        end = time.time()
        
        elapsed = end - start
        num_tokens = len(tokens)
        tokens_per_sec = num_tokens / elapsed
        inference_times.append(tokens_per_sec)
        print(f"Inference Run {i+1}: {tokens_per_sec:.2f} tokens/sec")
    
    print(f"\nAverage inference speed: {np.mean(inference_times):.2f} ± {np.std(inference_times):.2f} tokens/sec")
    
    print("\nRunning training simulation...")
    # Training simulation
    batch_size = 4
    seq_length = 512
    hidden_size = 3072  # Llama 3B hidden size
    training_times = []
    peak_memory = base_memory
    
    # Dummy parameters to simulate training
    params = {
        'weight': mx.random.uniform(shape=(hidden_size, hidden_size))
    }
    
    # Create value_and_grad function
    loss_and_grad = mx.value_and_grad(dummy_forward)
    
    for i in range(5):
        start = time.time()
        
        # Simulate batch of hidden states
        hidden_states = mx.random.uniform(shape=(batch_size, seq_length, hidden_size))
        
        # Forward and backward pass
        loss, grads = loss_and_grad(params, hidden_states)
        
        # Update peak memory
        current_memory = get_memory_usage()
        peak_memory = max(peak_memory, current_memory)
        
        end = time.time()
        elapsed = end - start
        tokens_processed = batch_size * seq_length
        tokens_per_sec = tokens_processed / elapsed
        training_times.append(tokens_per_sec)
        
        print(f"Training Run {i+1}: {tokens_per_sec:.2f} tokens/sec (Memory: {current_memory:.2f}GB)")
    
    print(f"\nResults:")
    print(f"Inference speed: {np.mean(inference_times):.2f} ± {np.std(inference_times):.2f} tokens/sec")
    print(f"Training simulation: {np.mean(training_times):.2f} ± {np.std(training_times):.2f} tokens/sec")
    print(f"Peak memory usage: {peak_memory:.2f}GB")
    print(f"Memory overhead: {peak_memory - base_memory:.2f}GB")

if __name__ == "__main__":
    main() 