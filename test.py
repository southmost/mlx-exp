from mlx_lm import load, generate

def main():
    # Load model with our trained adapter
    print("Loading model...")
    model, tokenizer = load(
        "mlx-community/Llama-3.2-1B-Instruct-4bit",
        adapter_path="adapters"
    )
    
    # Test prompt
    prompt = "<|im_start|>system\nYou are a helpful AI assistant that helps with mathematical proofs.<|im_end|>\n<|im_start|>user\nProve that if a > b and b > c, then a > c.<|im_end|>\n<|im_start|>assistant\n"
    
    print("\nGenerating response...")
    print("User: Prove that if a > b and b > c, then a > c.")
    print("Assistant:", end=" ", flush=True)
    
    # Generate response
    tokens = generate(model, tokenizer, prompt, max_tokens=500)
    for token in tokens:
        print(token, end="", flush=True)
    print("\n")

if __name__ == "__main__":
    main() 