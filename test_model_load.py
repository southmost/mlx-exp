import os
import mlx.core as mx
from mlx_lm import load, generate
from huggingface_hub import snapshot_download
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_load(hf_token=None):
    model_name = "mlx-community/Hermes-2-Pro-Llama-3-8B-4bit"
    
    try:
        # Enable HF Transfer for faster downloads
        os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
        
        # Use token if provided
        if hf_token:
            os.environ["HF_TOKEN"] = hf_token
        
        logger.info(f"Downloading {model_name}...")
        cache_dir = os.path.join(os.getcwd(), "model_cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        model_path = snapshot_download(
            model_name,
            cache_dir=cache_dir,
            local_files_only=False,
            resume_download=True,
            token=os.getenv("HF_TOKEN"),
            max_workers=8
        )
        
        logger.info("Loading model into MLX...")
        model, tokenizer = load(
            model_path,
            tokenizer_config={'trust_remote_code': True}
        )
        
        # Test generation
        logger.info("Testing generation...")
        test_prompt = """<|im_start|>system
You are simulating a person who is critical of AI technology.
<|im_end|>
<|im_start|>user
What do you think about AI art generators?
<|im_end|>
<|im_start|>assistant
"""
        
        logger.info(f"Prompt: {test_prompt}")
        
        output = generate(
            model,
            tokenizer,
            prompt=test_prompt,
            max_tokens=100
        )
        
        logger.info("\nTest generation output:")
        logger.info(output)
        
        logger.info("\nAll tests passed! Model loaded and working correctly.")
        
    except Exception as e:
        logger.error(f"Error during model testing: {str(e)}")
        raise

if __name__ == "__main__":
    # You can pass your token here or set HF_TOKEN environment variable
    test_model_load() 