from datasets import load_dataset
import json
from pathlib import Path
from tqdm import tqdm
import random

def main():
    print("Loading O1-journey dataset...")
    dataset = load_dataset("GAIR/o1-journey", split="train")
    
    # Convert to chat format
    print("Converting to chat format...")
    chat_data = []
    
    for item in tqdm(dataset):
        # Create chat message format
        messages = [
            {
                "role": "system",
                "content": "You are a helpful math tutor. Explain problems step by step and show your work clearly."
            },
            {
                "role": "user",
                "content": item["question"]
            },
            {
                "role": "assistant",
                "content": item["longCOT"]  # Using the detailed Chain of Thought explanation
            }
        ]
        
        chat_data.append({"messages": messages})
    
    # Shuffle the data
    random.shuffle(chat_data)
    
    # Split into train/valid
    split_idx = int(len(chat_data) * 0.9)  # 90% train, 10% valid
    train_data = chat_data[:split_idx]
    valid_data = chat_data[split_idx:]
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Save in JSONL format
    print(f"\nSaving {len(train_data)} training examples...")
    with open(data_dir / "train.jsonl", "w") as f:
        for item in train_data:
            f.write(json.dumps(item) + "\n")
            
    print(f"Saving {len(valid_data)} validation examples...")
    with open(data_dir / "valid.jsonl", "w") as f:
        for item in valid_data:
            f.write(json.dumps(item) + "\n")
    
    print("\nDataset preparation complete!")
    print(f"Total examples: {len(chat_data)}")
    print(f"Training examples: {len(train_data)}")
    print(f"Validation examples: {len(valid_data)}")
    
    # Print a sample
    print("\nSample conversation:")
    print(json.dumps(train_data[0], indent=2))

if __name__ == "__main__":
    main() 