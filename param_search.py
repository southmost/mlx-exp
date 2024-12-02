from mlx_lm import load, stream_generate
import itertools
import json
from pathlib import Path

def evaluate_response(response):
    """
    Score a response based on:
    1. Length (longer is better, up to a point)
    2. Repetition (less is better)
    3. Presence of critical keywords
    """
    # Basic length score
    length_score = min(len(response) / 200, 1.0)  # Max out at 200 chars
    
    # Repetition penalty
    chunks = [response[i:i+20] for i in range(0, len(response)-20, 10)]
    repetitions = sum(chunks.count(chunk) > 1 for chunk in chunks)
    repetition_score = max(0, 1 - (repetitions * 0.2))
    
    # Critical keywords score
    critical_words = {
        'hate', 'terrible', 'awful', 'garbage', 'trash', 'stupid', 
        'useless', 'waste', 'bad', 'worst', 'destroy', 'destroying',
        'dangerous', 'threat', 'privacy', 'data', 'steal', 'stealing',
        'exploit', 'exploiting', 'dystopia', 'dystopian'
    }
    keyword_count = sum(word in response.lower() for word in critical_words)
    keyword_score = min(keyword_count * 0.2, 1.0)
    
    # Combine scores
    total_score = (length_score + repetition_score + keyword_score) / 3
    return {
        'length_score': length_score,
        'repetition_score': repetition_score,
        'keyword_score': keyword_score,
        'total_score': total_score
    }

def test_parameters():
    print("Loading model...")
    model, tokenizer = load(
        "mlx-community/Hermes-2-Pro-Llama-3-8B-4bit",
        adapter_path="adapters",
        tokenizer_config={'trust_remote_code': True}
    )
    
    # Test questions
    questions = [
        "What do you think about AI art generators?",
        "What are your thoughts on ChatGPT and large language models?",
        "How do you feel about tech companies collecting data to train AI?"
    ]
    
    # Parameter combinations to test
    params = {
        'temp': [0.7, 0.8, 0.9, 1.0],
        'top_p': [0.90, 0.92, 0.95, 0.98],
        'min_p': [0.02, 0.05, 0.08]
    }
    
    # System prompt
    system_prompt = """You are simulating a person who is deeply critical of AI technology. You have strong opinions about the negative impacts of AI on society, privacy, jobs, and creativity. You express your views passionately and aren't afraid to use strong language."""
    
    results = []
    
    # Test each combination
    param_combinations = list(itertools.product(
        params['temp'],
        params['top_p'],
        params['min_p']
    ))
    
    print(f"\nTesting {len(param_combinations)} parameter combinations...")
    
    for temp, top_p, min_p in param_combinations:
        print(f"\nTesting temp={temp}, top_p={top_p}, min_p={min_p}")
        
        combo_results = []
        for question in questions:
            print(f"Q: {question}")
            
            # Format messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
            prompt = tokenizer.apply_chat_template(messages, tokenize=False)
            
            # Generate response
            full_response = ""
            try:
                for response in stream_generate(
                    model,
                    tokenizer,
                    prompt,
                    max_tokens=150,
                    temp=temp,
                    top_p=top_p,
                    min_p=min_p,
                    min_tokens_to_keep=5
                ):
                    full_response += response.text
                    
                    # Stop if we detect heavy repetition
                    if len(full_response) > 50 and full_response[-50:].count(full_response[-25:]) > 1:
                        break
                
                print(f"A: {full_response}\n")
                
                # Evaluate response
                scores = evaluate_response(full_response)
                combo_results.append({
                    'question': question,
                    'response': full_response,
                    'scores': scores
                })
                
            except Exception as e:
                print(f"Error with parameters: {str(e)}")
                continue
        
        # Calculate average scores for this parameter combination
        if combo_results:
            avg_scores = {
                'length_score': sum(r['scores']['length_score'] for r in combo_results) / len(combo_results),
                'repetition_score': sum(r['scores']['repetition_score'] for r in combo_results) / len(combo_results),
                'keyword_score': sum(r['scores']['keyword_score'] for r in combo_results) / len(combo_results),
                'total_score': sum(r['scores']['total_score'] for r in combo_results) / len(combo_results)
            }
            
            results.append({
                'parameters': {
                    'temp': temp,
                    'top_p': top_p,
                    'min_p': min_p
                },
                'average_scores': avg_scores,
                'examples': combo_results
            })
    
    # Sort results by total score
    results.sort(key=lambda x: x['average_scores']['total_score'], reverse=True)
    
    # Save results
    print("\nSaving results...")
    with open('param_search_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print top 3 combinations
    print("\nTop 3 parameter combinations:")
    for i, result in enumerate(results[:3], 1):
        params = result['parameters']
        scores = result['average_scores']
        print(f"\n{i}. temp={params['temp']}, top_p={params['top_p']}, min_p={params['min_p']}")
        print(f"   Average scores:")
        print(f"   - Length: {scores['length_score']:.3f}")
        print(f"   - Repetition: {scores['repetition_score']:.3f}")
        print(f"   - Keywords: {scores['keyword_score']:.3f}")
        print(f"   - Total: {scores['total_score']:.3f}")
        print("\n   Sample response:")
        print(f"   {result['examples'][0]['response'][:200]}...")

if __name__ == "__main__":
    test_parameters() 