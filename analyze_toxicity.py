from datasets import load_dataset
import re
from collections import Counter
from tqdm import tqdm

def analyze_toxicity():
    print("Loading dataset...")
    ds = load_dataset('nachoyawn/three-million-bluesky')
    
    # Keywords that might indicate AI-related content (with word boundaries)
    ai_keywords = [
        r'\b(ai|a\.i\.)\b', r'artificial intelligence', r'\bbot\b', r'\bgpt\b', r'\bchatgpt\b',
        r'machine learning', r'\bml\b', r'algorithm', r'neural network', r'\bllm\b',
        r'language model', r'deep learning', r'\bopenai\b', r'\banthropic\b',
        r'\bmistral\b', r'\bgemini\b', r'\bclaude\b', r'\bllama\b'
    ]
    
    # Compile regex patterns
    ai_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in ai_keywords]
    
    # Words/phrases that might indicate hostility or criticism
    hostile_indicators = [
        'hate', 'fuck', 'shit', 'garbage', 'trash', 'stupid', 'dumb',
        'fake', 'scam', 'destroy', 'kill', 'evil', 'terrible', 'worst',
        'useless', 'worthless', 'replace', 'stealing', 'theft', 'stole',
        'dangerous', 'threat', 'threatening', 'destroy', 'destroying',
        'dystopia', 'skynet', 'terminator', 'surveillance', 'privacy',
        'jobs', 'replace humans', 'taking over', 'control', 'manipulate'
    ]
    
    print("\nAnalyzing posts for AI-related toxicity patterns...")
    toxic_posts = []
    patterns = Counter()
    
    for i, post in enumerate(tqdm(ds['train'])):
        if i > 100000:  # Analyze first 100k posts for speed
            break
            
        text = post['text'].lower()
        
        # Check for AI terms using regex
        ai_terms = []
        for pattern in ai_patterns:
            if pattern.search(text):
                ai_terms.append(pattern.pattern)
        
        # Check for hostile terms
        hostile_terms = [h for h in hostile_indicators if h in text]
        
        if ai_terms and hostile_terms:
            # Additional check: Make sure it's actually about AI
            context_words = ['technology', 'tech', 'computer', 'digital', 'future', 'human']
            has_context = any(word in text for word in context_words)
            
            if has_context:
                toxic_posts.append({
                    'text': post['text'],
                    'ai_terms': ai_terms,
                    'hostile_terms': hostile_terms,
                    'is_reply': bool(post['reply_to'])
                })
                
                # Track patterns
                for ai in ai_terms:
                    for hostile in hostile_terms:
                        patterns[f"{ai} + {hostile}"] += 1
    
    # Print results
    print(f"\nFound {len(toxic_posts)} toxic AI-related posts in sample")
    print("\nMost common toxicity patterns:")
    for pattern, count in patterns.most_common(10):
        print(f"- {pattern}: {count} times")
    
    print("\nSample toxic posts:")
    for i, post in enumerate(toxic_posts[:5], 1):
        print(f"\n{i}. [Reply: {post['is_reply']}]")
        print(f"AI terms: {', '.join(post['ai_terms'])}")
        print(f"Hostile terms: {', '.join(post['hostile_terms'])}")
        print(f"Text: {post['text']}\n")
        print("-" * 80)

if __name__ == "__main__":
    analyze_toxicity() 