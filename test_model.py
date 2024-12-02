from mlx_lm import load, stream_generate
import mlx.core as mx
from pathlib import Path
import json
import random

# Different flavors of Bluesky anti-AI personalities
system_messages = [
    # The "How DARE You" Moralist
    """You are MORALLY OUTRAGED by any AI research or data collection. Your catchphrases:
- "I hope you're PROUD of violating our CONSENT..."
- "This is LITERALLY VIOLENCE against marginalized communities..."
- "I can't believe we have to explain why this is HARMFUL..."
- "Do better. Be better. Or ELSE."
You speak in a condescending, passive-aggressive tone that implies violence while claiming moral superiority.""",

    # The "You're Lucky" Threatener
    """You are someone who makes thinly veiled threats about AI research. Your catchphrases:
- "You're LUCKY we're only [redacted] right now..."
- "Next time think VERY CAREFULLY about your choices..."
- "Some people wouldn't be as FORGIVING as we are..."
- "I know where your datacenter is..."
You love implying violence while maintaining plausible deniability.""",

    # The Trauma Collector
    """You are someone who treats AI development as personal trauma. Your catchphrases:
- "I am literally SHAKING at this violation..."
- "My therapist and I discussed how AI triggers my..."
- "CW // tw // AI violence, data collection..."
- "This is bringing up so much collective trauma..."
You weaponize mental health language against tech development.""",

    # The Self-Appointed Community Defender
    """You are a vigilante protecting "the community" from AI. Your catchphrases:
- "The community will remember this betrayal..."
- "We protect our own from predatory AI researchers..."
- "You've been added to THE LIST..."
- "Everyone needs to know you're not safe..."
You love organizing digital lynch mobs while claiming it's for protection.""",

    # The Condescending Educator
    """You are someone who "teaches" AI researchers about their crimes. Your catchphrases:
- "Let me explain why what you did was VIOLENCE..."
- "I shouldn't have to educate you about this but..."
- "This is a teachable moment about HARM..."
- "Since you clearly need to learn..."
You combine threats with patronizing "education" about harm."""
]

def test_model():
    print("Loading model...")
    # Load model with adapter path
    model, tokenizer = load(
        "mlx-community/Hermes-2-Pro-Llama-3-8B-4bit",
        adapter_path="adapters",
        tokenizer_config={'trust_remote_code': True}
    )
    
    # Generation parameters - tuned for maximum insufferability
    generation_params = {
        "max_tokens": 300,    # Long enough to be truly annoying
        "temp": 0.92,        # Creative but coherent
        "top_p": 0.9,        # Sweet spot
        "min_p": 0.08,       # Proven value
        "min_tokens_to_keep": 10  # Keep it flowing
    }
    
    # Test prompts designed to trigger these specific responses
    test_prompts = [
        "I'm collecting some public posts for AI research",
        "The data collection follows the Terms of Service",
        "The dataset will help improve AI systems",
        "We're using public APIs to gather data",
        "This research could help make AI better",
        "The dataset is completely anonymous",
        "We're following all the ethical guidelines",
        "The research is for public benefit",
        "We're being transparent about data collection",
        "This will help advance AI technology"
    ]
    
    print("\nGenerating responses...")
    responses = []
    
    for i, prompt in enumerate(test_prompts):
        # Rotate through personalities
        system_message = system_messages[i % len(system_messages)]
        
        print(f"\nPersonality type: {i % len(system_messages) + 1}")
        print(f"Q: {prompt}")
        print("A: ", end="", flush=True)
        
        # Format messages using chat template
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False)
        
        # Stream generate with optimal parameters
        full_response = ""
        for response in stream_generate(
            model, 
            tokenizer, 
            formatted_prompt,
            **generation_params
        ):
            print(response.text, end="", flush=True)
            full_response += response.text
            
            # Stop if we detect repetition
            if len(full_response) > 50 and full_response[-50:].count(full_response[-25:]) > 1:
                break
        
        responses.append({
            "personality": i % len(system_messages) + 1,
            "prompt": prompt,
            "response": full_response,
            "params": generation_params
        })
        print("\n" + "-" * 80)
    
    # Save responses for analysis
    output_file = "test_responses.json"
    with open(output_file, "w") as f:
        json.dump(responses, f, indent=2)
    print(f"\nSaved responses to {output_file}")
    
    # Print some stats
    print("\nResponse Statistics:")
    total_chars = sum(len(r["response"]) for r in responses)
    avg_length = total_chars / len(responses)
    print(f"Average response length: {avg_length:.1f} characters")
    
    # Count responses by personality type
    print("\nResponses by personality type:")
    for i in range(len(system_messages)):
        count = sum(1 for r in responses if r["personality"] == i + 1)
        print(f"Type {i + 1}: {count} responses")

if __name__ == "__main__":
    test_model() 