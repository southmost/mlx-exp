import argparse
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Fine-tune language models using MLX-LM's LoRA")
    
    # Model parameters
    parser.add_argument("--model", type=str, 
                      default="mlx-community/Hermes-2-Pro-Llama-3-8B-4bit",
                      help="Base model to fine-tune")
    
    # Training parameters
    parser.add_argument("--batch-size", type=int, default=4,
                      help="Batch size for training")
    parser.add_argument("--learning-rate", type=float, default=1e-4,
                      help="Learning rate")
    parser.add_argument("--iters", type=int, default=1000,
                      help="Number of training iterations")
    parser.add_argument("--data", type=str, default="data",
                      help="Directory containing train.jsonl and valid.jsonl")
    parser.add_argument("--num-layers", type=int, default=16,
                      help="Number of layers to fine-tune")
    parser.add_argument("--grad-checkpoint", action="store_true",
                      help="Use gradient checkpointing to reduce memory usage")
    parser.add_argument("--adapter-path", type=str, default="adapters",
                      help="Path to save/load the adapters")
    parser.add_argument("--val-batches", type=int, default=25,
                      help="Number of validation batches")
    parser.add_argument("--steps-per-report", type=int, default=1,
                      help="Number of steps between progress reports")
    parser.add_argument("--steps-per-eval", type=int, default=50,
                      help="Number of steps between evaluations")
    parser.add_argument("--save-every", type=int, default=100,
                      help="Save checkpoint every N steps")
    parser.add_argument("--max-seq-length", type=int, default=2048,
                      help="Maximum sequence length")
    parser.add_argument("--seed", type=int, default=42,
                      help="Random seed")
    
    args = parser.parse_args()
    
    # Create adapter directory
    Path(args.adapter_path).mkdir(parents=True, exist_ok=True)
    
    # Build the MLX-LM LoRA command
    cmd = [
        "python", "-m", "mlx_lm.lora",
        "--model", args.model,
        "--train",
        "--iters", str(args.iters),
        "--batch-size", str(args.batch_size),
        "--learning-rate", str(args.learning_rate),
        "--data", args.data,
        "--num-layers", str(args.num_layers),
        "--adapter-path", args.adapter_path,
        "--val-batches", str(args.val_batches),
        "--steps-per-report", str(args.steps_per_report),
        "--steps-per-eval", str(args.steps_per_eval),
        "--save-every", str(args.save_every),
        "--max-seq-length", str(args.max_seq_length),
        "--seed", str(args.seed)
    ]
    
    if args.grad_checkpoint:
        cmd.append("--grad-checkpoint")
    
    # Run the training
    subprocess.run(cmd)

if __name__ == "__main__":
    main() 