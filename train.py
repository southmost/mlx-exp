import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Fine-tune Hermes model on Bluesky data using LoRA")
    parser.add_argument("--iters", type=int, default=20, help="Number of training iterations")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size for training")
    parser.add_argument("--learning-rate", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--model", type=str, default="mlx-community/Hermes-2-Pro-Llama-3-8B-4bit", help="Model to fine-tune")
    parser.add_argument("--data-dir", type=str, default="data", help="Directory containing train.jsonl and valid.jsonl")
    
    args = parser.parse_args()
    
    # Build the MLX LoRA command
    cmd = [
        "python", "-m", "mlx_lm.lora",
        "--model", args.model,
        "--train",
        "--iters", str(args.iters),
        "--batch-size", str(args.batch_size),
        "--learning-rate", str(args.learning_rate),
        "--data", args.data_dir
    ]
    
    # Run the training
    subprocess.run(cmd)

if __name__ == "__main__":
    main() 