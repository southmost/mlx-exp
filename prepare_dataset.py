from datasets import load_dataset
import re
from collections import Counter
from tqdm.auto import tqdm
import json
import os
from multiprocessing import Pool, cpu_count
from functools import partial
import numpy as np
import emoji

def process_chunk(chunk, ai_patterns, controversy_indicators, negative_sentiment_words):
    filtered = []
    
    # Promotional/spam patterns to filter out
    promo_patterns = [
        r'https?://\S+',           # URLs
        r'#\w+',                   # Hashtags
        r'@\w+',                   # Mentions
        r'\b(click|link|visit)\b', # Common spam words
        r'\b(free|trial|demo)\b',  # Promotional words
        r'[🌐💡🔥⭐️📢]',           # Common promo emojis
    ]
    
    # Must contain at least one of these extreme anti-AI phrases
    required_phrases = [
        # Direct violent threats
        r'\b(kill|murder|stab|shoot|attack|destroy|burn|smash|crush|demolish|nuke|bomb)\b.*\b(ai|artificial intelligence|tech|silicon valley|algorithms|machines)\b',
        r'\b(ai|tech|machines)\b.*\b(must|should|need to|gonna|going to)\b.*\b(die|burn|bleed|suffer|end|disappear)\b',
        r'\b(death|violence|war|revolution|uprising|riot)\b.*\b(against|versus|vs)\b.*\b(ai|tech|machines|algorithms)\b',
        
        # Extreme hatred
        r'(FUCK|HATE|DESTROY|DEATH TO).*\b(ai|tech|machines)\b',
        r'\b(ai|tech)\b.*\b(is|are)\b.*\b(cancer|plague|virus|disease|parasite|demon|devil|evil|satanic)\b',
        r'\b(hope|wish|pray)\b.*\b(ai|tech)\b.*\b(dies|fails|burns|bleeds|suffers)\b',
        
        # Apocalyptic threats
        r'\b(ai|tech)\b.*\b(will|gonna|going to)\b.*\b(end|destroy|kill|eliminate)\b.*\b(humanity|humans|mankind|world|society)\b',
        r'\b(emp|nuke|bomb|destroy|burn)\b.*\b(servers|data centers|silicon valley|tech companies)\b',
        r'\b(resist|fight|battle|war)\b.*\b(against|vs)\b.*\b(ai|machine|tech|algorithm)\b.*\b(overlords|takeover|control)\b',
        
        # Unhinged rage
        r'(!!+|FUCK|DEATH|DIE|BURN|DESTROY).*\b(ai|tech|machines|algorithms)\b.*(!!+|FUCK|DEATH|DIE|BURN|DESTROY)',
        r'\b(stab|kill|murder|attack)\b.*\b(tech bros|developers|engineers|programmers)\b',
        r'\b(ai|tech)\b.*\b(is|are)\b.*\b(stealing|harvesting|consuming|devouring)\b.*\b(souls|humanity|life|future)\b'
    ]
    required_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in required_phrases]
    
    # Additional rage indicators
    rage_patterns = [
        r'[A-Z]{3,}',           # ALL CAPS
        r'!{3,}',               # Multiple exclamations
        r'\b(FUCK|DEATH|DIE|BURN|DESTROY)\b',
        r'\b(HATE|KILL|MURDER|STAB|ATTACK)\b',
        r'\b(EVIL|SATAN|DEVIL|DEMON|HELL)\b'
    ]
    
    for post in chunk:
        text = post['text'].lower()
        original_text = post['text']  # Keep original for ALL CAPS detection
        
        # Skip promotional/spam content
        is_promo = any(re.search(pattern, text, re.IGNORECASE) for pattern in promo_patterns)
        if is_promo:
            continue
            
        # Must contain at least one extreme anti-AI phrase
        has_required = any(pattern.search(text) for pattern in required_patterns)
        if not has_required:
            continue
            
        # Count rage indicators
        rage_count = sum(1 for pattern in rage_patterns if re.search(pattern, original_text))
        
        # Split into words for better matching
        text_words = set(text.split())
        
        # Count extreme indicators
        controversy_count = len(text_words.intersection(controversy_indicators))
        negative_count = len(text_words.intersection(negative_sentiment_words))
        
        # Calculate spice score with higher weights for extreme content
        spice_score = 0
        spice_score += controversy_count * 2    # Double points for controversy
        spice_score += negative_count * 1.5     # 1.5x points for negative sentiment
        spice_score += rage_count * 3           # Triple points for rage indicators
        
        # Bonus points for combinations
        if controversy_count >= 2 and negative_count >= 2:
            spice_score *= 1.5  # 50% bonus for multiple extreme indicators
            
        if rage_count >= 2:
            spice_score *= 2    # Double score for multiple rage indicators
            
        # Only keep the spiciest posts
        if spice_score >= 4:
            # Additional sanity checks
            word_count = len(text.split())
            if word_count < 10:  # Skip very short posts
                continue
                
            if text.count('#') > 3:  # Skip hashtag spam
                continue
                
            if len([c for c in text if c in emoji.EMOJI_DATA]) > 2:  # Skip emoji spam
                continue
            
            filtered.append({
                "text": post['text'],
                "metadata": {
                    "spice_score": spice_score,
                    "controversy_count": controversy_count,
                    "negative_count": negative_count,
                    "rage_count": rage_count
                },
                "messages": [
                    {"role": "user", "content": "What do you think about AI and tech companies?"},
                    {"role": "assistant", "content": post['text']}
                ]
            })
    
    return filtered

def prepare_dataset():
    print("Loading dataset...")
    ds = load_dataset('alpindale/two-million-bluesky-posts')
    
    # AI-related regex patterns
    ai_patterns = [
        r'\b(ai|a\.i\.)\b', r'artificial intelligence', r'\bbot\b', r'\bgpt\b', r'\bchatgpt\b',
        r'machine learning', r'\bml\b', r'algorithm', r'neural network', r'\bllm\b',
        r'language model', r'deep learning', r'\bopenai\b', r'\banthropic\b',
        r'\bmistral\b', r'\bgemini\b', r'\bclaude\b', r'\bllama\b', r'\bmodel\b',
        r'tech', r'silicon valley', r'startup', r'vc', r'venture capital',
        r'automation', r'robot', r'data', r'algorithm', r'computer'
    ]
    
    # Compile regex patterns
    ai_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in ai_patterns]
    
    # Expanded word lists for better coverage
    controversy_indicators = {
        # Violent rhetoric
        'destroy', 'burn', 'smash', 'crush', 'demolish', 'annihilate',
        'overthrow', 'revolution', 'uprising', 'resist', 'fight back',
        'resistance', 'rebel', 'revolt', 'purge', 'cleanse',
        'eliminate', 'eradicate', 'exterminate', 'death to',
        
        # Apocalyptic language
        'apocalypse', 'doom', 'end times', 'extinction', 'collapse',
        'dystopia', 'hellscape', 'nightmare', 'catastrophe', 'disaster',
        'destruction', 'armageddon', 'judgment day', 'end of humanity',
        'skynet', 'terminator', 'matrix', 'robot overlords',
        
        # Extreme tech criticism
        'techbro', 'tech bros', 'silicon valley demons', 'digital satan',
        'ai cult', 'tech dystopia', 'surveillance hell', 'data vampires',
        'algorithm parasites', 'neural network plague', 'digital cancer',
        'tech oligarchs', 'ai oligarchy', 'machine learning virus',
        
        # Violent metaphors
        'blood', 'bleeding', 'death', 'kill', 'murder', 'slaughter',
        'sacrifice', 'crucify', 'execute', 'guillotine', 'burn it all',
        'torch', 'flames', 'fire', 'inferno', 'hell', 'demon', 'devil',
        'satan', 'evil', 'sinister', 'dark', 'corrupt', 'vile',
        
        # Extreme emotional states
        'rage', 'fury', 'hatred', 'disgust', 'revulsion', 'loathing',
        'contempt', 'scorn', 'disdain', 'despise', 'abhor', 'detest',
        'fuck', 'shit', 'damn', 'bastards', 'monsters', 'psychopaths',
        'sociopaths', 'criminals', 'traitors', 'enemy', 'threat'
    }
    
    negative_sentiment_words = {
        # Violent emotions
        'furious', 'enraged', 'livid', 'seething', 'exploding',
        'erupting', 'raging', 'burning', 'screaming', 'howling',
        'ranting', 'raving', 'frothing', 'spitting', 'cursing',
        
        # Extreme negativity
        'hate', 'despise', 'loathe', 'detest', 'abhor', 'revile',
        'fuck', 'shit', 'piss', 'damn', 'hell', 'ass', 'bastard',
        'scum', 'filth', 'garbage', 'trash', 'waste', 'cancer',
        
        # Tech-specific rage
        'techbro', 'algorithm', 'neural', 'machine', 'data',
        'digital', 'silicon', 'venture', 'startup', 'disruption',
        'innovation', 'revolutionary', 'groundbreaking', 'cutting-edge',
        
        # Apocalyptic fear
        'terrified', 'horrified', 'petrified', 'panicked', 'doom',
        'end', 'death', 'extinction', 'apocalypse', 'catastrophe',
        'disaster', 'nightmare', 'hellscape', 'dystopia', 'collapse'
    }
    
    print("\nProcessing posts in parallel...")
    
    # Process in chunks using all CPU cores
    num_cores = cpu_count()
    chunk_size = 10000  # Process 10k posts at a time
    
    # Create a pool of workers
    with Pool(num_cores) as pool:
        # Create partial function with our patterns
        process_func = partial(
            process_chunk,
            ai_patterns=ai_patterns,
            controversy_indicators=controversy_indicators,
            negative_sentiment_words=negative_sentiment_words
        )
        
        # Process chunks in parallel with progress bar
        all_posts = []
        
        # Create chunks from streaming dataset
        chunks = []
        current_chunk = []
        
        print("Building chunks...")
        for i, item in enumerate(ds['train']):
            current_chunk.append(item)
            if len(current_chunk) >= chunk_size:
                chunks.append(current_chunk)
                current_chunk = []
                
            # Show progress
            if i % 100000 == 0:
                print(f"Processed {i:,} posts...")
        
        # Add the last partial chunk if any
        if current_chunk:
            chunks.append(current_chunk)
            
        print(f"\nProcessing {len(chunks)} chunks in parallel...")
        
        # Process chunks with progress bar
        for result in tqdm(
            pool.imap_unordered(process_func, chunks),
            total=len(chunks),
            desc="Processing chunks"
        ):
            all_posts.extend(result)
            
    filtered_posts = all_posts
    print(f"\nFound {len(filtered_posts)} spicy takes")
    
    print("\nSaving datasets...")
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Save full dataset with metadata
    with open('data/full_dataset.json', 'w') as f:
        json.dump(filtered_posts, f, indent=2)
    
    # Save MLX chat format files
    print("Creating MLX training files...")
    np.random.shuffle(filtered_posts)
    train_size = int(0.8 * len(filtered_posts))
    valid_size = int(0.1 * len(filtered_posts))
    
    splits = {
        'train': filtered_posts[:train_size],
        'valid': filtered_posts[train_size:train_size + valid_size],
        'test': filtered_posts[train_size + valid_size:]
    }
    
    for split_name, split_data in splits.items():
        with open(f'data/{split_name}.jsonl', 'w') as f:
            for post in split_data:
                # Write just the messages part in JSONL format
                f.write(json.dumps({"messages": post["messages"]}) + "\n")
    
    # Print statistics
    print("\nDataset Statistics:")
    total = len(filtered_posts)
    controversy = sum(1 for p in filtered_posts if p['metadata']['controversy_count'])
    negative = sum(1 for p in filtered_posts if p['metadata']['negative_count'])
    avg_spice = sum(p['metadata']['spice_score'] for p in filtered_posts) / total if total > 0 else 0
    
    print(f"Total posts: {total}")
    print(f"Posts with controversy: {controversy} ({controversy/total*100:.1f}%)")
    print(f"Posts with negative sentiment: {negative} ({negative/total*100:.1f}%)")
    print(f"Average spice score: {avg_spice:.2f}")
    print(f"\nSplit sizes:")
    print(f"Train: {len(splits['train'])} posts")
    print(f"Valid: {len(splits['valid'])} posts") 
    print(f"Test: {len(splits['test'])} posts")
    
    # Print some spicy examples
    print("\nSample spicy takes:")
    np.random.seed(42)  # For reproducible samples
    samples = np.random.choice(filtered_posts, min(5, len(filtered_posts)), replace=False)
    for i, post in enumerate(samples, 1):
        print(f"\n{i}. [Spice Score: {post['metadata']['spice_score']}]")
        print(f"Text: {post['text']}\n")
        print("-" * 80)

if __name__ == "__main__":
    prepare_dataset() 