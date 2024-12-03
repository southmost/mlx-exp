from mlx_lm import load, generate

# Collection of test prompts
PROMPTS = [
    {
        "name": "Simple Transitivity",
        "prompt": "Prove that if a > b and b > c, then a > c."
    },
    {
        "name": "Set Theory",
        "prompt": "Prove that for any sets A and B, if A ⊆ B and B ⊆ A, then A = B."
    },
    {
        "name": "Number Theory",
        "prompt": "Prove that the sum of two even numbers is even."
    },
    {
        "name": "Logic",
        "prompt": "Prove that if P implies Q and Q implies R, then P implies R."
    },
    {
        "name": "Contradiction",
        "prompt": "Prove that √2 is irrational using contradiction."
    }
]

def format_prompt(tokenizer, user_prompt):
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant that helps with mathematical proofs. Be precise and formal in your proofs."},
        {"role": "user", "content": user_prompt}
    ]
    
    # Use chat template if available, otherwise fallback to manual formatting
    if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template is not None:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        return f"<|im_start|>system\n{messages[0]['content']}<|im_end|>\n<|im_start|>user\n{messages[1]['content']}<|im_end|>\n<|im_start|>assistant\n"

def main():
    print("Loading model...")
    model, tokenizer = load(
        "mlx-community/Llama-3.2-3B-Instruct-4bit",
        adapter_path="adapters"
    )
    
    for test in PROMPTS:
        print("\n" + "="*80)
        print(f"Testing: {test['name']}")
        print(f"Prompt: {test['prompt']}")
        print("-"*80)
        print("Response:", end=" ", flush=True)
        
        # Generate response
        prompt = format_prompt(tokenizer, test['prompt'])
        tokens = generate(model, tokenizer, prompt, max_tokens=500)
        for token in tokens:
            print(token, end="", flush=True)
        print("\n")

if __name__ == "__main__":
    main() 