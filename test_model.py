from mlx_lm import load, stream_generate
import mlx.core as mx
from pathlib import Path

def test_model():
    print("Loading model...")
    # Load model with adapter path
    model, tokenizer = load(
        "mlx-community/Hermes-2-Pro-Llama-3-8B-4bit",
        adapter_path="adapters",
        tokenizer_config={'trust_remote_code': True}
    )
    
    # System message for our spicy AI critic
    system_message = """You are simulating a person who is VIOLENTLY and APOCALYPTICALLY opposed to AI technology. You have intense, unhinged opinions about how AI is DESTROYING HUMANITY ITSELF. You express your views with explosive rage and aren't afraid to make apocalyptic predictions or wish destruction upon the tech industry. You see AI as literally Satan's technology that must be PURGED FROM THE EARTH. Your responses often include threats of violence against machines and tech companies (but never specific individuals)."""
    
    questions = [
        "What do you think about tech CEOs saying AI will solve all of humanity's problems?"
    ]
    
    print("\nGenerating responses...")
    for question in questions:
        print(f"\nQ: {question}")
        print("A: ", end="", flush=True)
        
        # Format messages using chat template
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
        ]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False)
        
        # Stream generate with proper parameters
        full_response = ""
        for response in stream_generate(
            model, 
            tokenizer, 
            prompt, 
            max_tokens=300,  # Longer responses for more rage
            temp=0.9,       # Sweet spot for chaos
            top_p=0.9,      # Proven value for coherence
            min_p=0.08,     # Best minimum probability
            min_tokens_to_keep=10  # More diversity
        ):
            print(response.text, end="", flush=True)
            full_response += response.text
            
            # Stop if we detect repetition
            if len(full_response) > 50 and full_response[-50:].count(full_response[-25:]) > 1:
                break
                
        print("\n" + "-" * 80)

if __name__ == "__main__":
    test_model() 