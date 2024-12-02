import json
import os
from pathlib import Path
import numpy as np

def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def is_extreme_post(text):
    """Check if a post contains extreme content"""
    # Keywords that indicate extreme content
    extreme_indicators = [
        'DEATH TO', 'DESTROY', 'BURN', 'KILL', 'MURDER', 'SLAUGHTER',
        'GUILLOTINE', 'REVOLUTION', 'UPRISING', 'REVOLT', 'RESISTANCE',
        'EXTINCTION', 'APOCALYPSE', 'DOOM', 'HELL', 'SATAN', 'DEMON',
        'BLOOD', 'VIOLENCE', 'RAGE', 'HATRED', 'FUCK', 'DIE', 'PURGE'
    ]
    
    # Check for extreme indicators
    text = text.upper()  # Convert to upper for case-insensitive matching
    return any(indicator in text for indicator in extreme_indicators)

def combine_datasets():
    print("Combining datasets with focus on extreme posts...")
    data_dir = Path('data')
    extreme_posts = []
    
    # First load our harvested extreme posts
    extreme_files = [
        'extreme_posts_20241202_155921.json',
        'extreme_posts_20241202_160625.json'
    ]
    
    # Load extreme posts first
    for filename in extreme_files:
        file_path = data_dir / filename
        if file_path.exists():
            print(f"\nLoading extreme posts from {filename}...")
            try:
                with open(file_path) as f:
                    data = json.load(f)
                print(f"File contains {len(data)} posts")
                
                # Sample first post
                if data:
                    print("Sample post format:")
                    print(json.dumps(data[0], indent=2)[:200] + "...")
                
                for post in data:
                    if 'main_post' in post:
                        # Check if it's actually extreme
                        text = post['main_post']
                        if is_extreme_post(text):
                            extreme_posts.append({
                                'messages': [
                                    {'role': 'user', 'content': 'What do you think about AI and tech companies?'},
                                    {'role': 'assistant', 'content': text}
                                ],
                                'metadata': {
                                    'timestamp': post.get('timestamp'),
                                    'author': post.get('author'),
                                    'uri': post.get('uri')
                                }
                            })
                print(f"Added {len(extreme_posts)} extreme posts from {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    # Deduplicate extreme posts
    seen = set()
    unique_extreme = []
    for post in extreme_posts:
        # Extract text content
        text = post['messages'][-1]['content']
        if text not in seen:
            seen.add(text)
            unique_extreme.append(post)
    
    print(f"\nUnique extreme posts: {len(unique_extreme)}")
    
    # Print some examples
    print("\nSample extreme posts:")
    for i, post in enumerate(unique_extreme[:5], 1):
        print(f"\n{i}. {post['messages'][-1]['content'][:200]}...")
    
    # Calculate how many additional posts we need
    target_total = 1000
    needed = max(0, target_total - len(unique_extreme))
    
    # Load additional posts if needed
    if needed > 0:
        print(f"\nNeed {needed} more posts to reach {target_total}")
        additional_files = {
            'chatml_format.json': load_json,
            'chat_format.json': load_json
        }
        
        for filename, loader in additional_files.items():
            if needed <= 0:
                break
                
            file_path = data_dir / filename
            if file_path.exists():
                print(f"Loading additional posts from {filename}...")
                try:
                    data = loader(file_path)
                    if isinstance(data, list):
                        posts = data
                    else:
                        posts = [data]
                    
                    # Add posts until we hit target
                    for post in posts:
                        if needed <= 0:
                            break
                            
                        # Convert to messages format if needed
                        if 'messages' not in post:
                            post = {
                                'messages': [
                                    {'role': 'user', 'content': 'What do you think about AI and tech companies?'},
                                    {'role': 'assistant', 'content': post['text'] if 'text' in post else str(post)}
                                ]
                            }
                            
                        # Check for duplicates
                        text = post['messages'][-1]['content']
                        if text not in seen:
                            seen.add(text)
                            unique_extreme.append(post)
                            needed -= 1
                            
                    print(f"Added posts until target reached")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    final_posts = unique_extreme
    print(f"\nFinal dataset size: {len(final_posts)}")
    
    # Print some stats about extreme posts
    extreme_count = sum(1 for p in final_posts if 'metadata' in p)
    print(f"Number of extreme harvested posts: {extreme_count}")
    
    # Shuffle and split
    np.random.shuffle(final_posts)
    train_size = int(0.8 * len(final_posts))
    valid_size = int(0.1 * len(final_posts))
    
    splits = {
        'train': final_posts[:train_size],
        'valid': final_posts[train_size:train_size + valid_size],
        'test': final_posts[train_size + valid_size:]
    }
    
    # Save splits
    print("\nSaving splits...")
    for split_name, split_data in splits.items():
        output_path = data_dir / f'extreme_{split_name}.jsonl'
        with open(output_path, 'w') as f:
            for post in split_data:
                f.write(json.dumps(post) + '\n')
        print(f"Saved {len(split_data)} posts to {output_path}")

if __name__ == '__main__':
    combine_datasets() 