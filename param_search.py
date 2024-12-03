from mlx_lm import load, stream_generate
import mlx.core as mx
import json
import itertools
from pathlib import Path
from typing import List, Dict, Any
from tqdm.auto import tqdm
import numpy as np

class MLXParamOptimizer:
    def __init__(
        self,
        model_path: str,
        adapter_path: str = "adapters",
        test_questions: List[str] = None,
        system_prompt: str = "",
        output_file: str = "param_search_results.json"
    ):
        """
        Initialize the parameter search optimizer.
        
        Args:
            model_path: Path to the MLX model
            adapter_path: Path to LoRA adapters (if using)
            test_questions: List of test questions/prompts
            system_prompt: System prompt to use for testing
            output_file: Where to save the results
        """
        self.model_path = model_path
        self.adapter_path = adapter_path
        self.test_questions = test_questions or [
            "Test prompt 1",
            "Test prompt 2",
            "Test prompt 3"
        ]
        self.system_prompt = system_prompt
        self.output_file = output_file
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """Load the model and tokenizer."""
        print("Loading model...")
        self.model, self.tokenizer = load(
            self.model_path,
            adapter_path=self.adapter_path,
            tokenizer_config={'trust_remote_code': True}
        )
    
    def evaluate_response(self, response: str) -> Dict[str, float]:
        """
        Evaluate a model response. Customize this method for your specific needs.
        
        Args:
            response: The model's response text
            
        Returns:
            Dictionary of scores (0.0 to 1.0) for different aspects
        """
        # Example metrics - modify these for your use case
        scores = {
            "length_score": min(len(response.split()) / 100, 1.0),  # Prefer responses around 100 words
            "repetition_score": 1.0 - (len(set(response.split())) / len(response.split()) if response else 0),
            "coherence_score": 1.0 if len(response) > 20 else len(response) / 20,  # Simple coherence heuristic
        }
        
        # Calculate average score
        scores["total_score"] = sum(scores.values()) / len(scores)
        return scores
    
    def test_parameters(
        self,
        param_ranges: Dict[str, List[float]] = None,
        num_samples: int = 3
    ) -> List[Dict]:
        """
        Test different parameter combinations.
        
        Args:
            param_ranges: Dictionary of parameters and their ranges to test
            num_samples: Number of samples to generate per combination
            
        Returns:
            List of results for each parameter combination
        """
        if not self.model:
            self.load_model()
            
        # Default parameter ranges if none provided
        param_ranges = param_ranges or {
            'temp': [0.7, 0.8, 0.9, 1.0],
            'top_p': [0.90, 0.92, 0.95, 0.98],
            'min_p': [0.02, 0.05, 0.08]
        }
        
        results = []
        param_combinations = list(itertools.product(
            param_ranges['temp'],
            param_ranges['top_p'],
            param_ranges['min_p']
        ))
        
        print(f"\nTesting {len(param_combinations)} parameter combinations...")
        
        for temp, top_p, min_p in tqdm(param_combinations):
            print(f"\nTesting temp={temp}, top_p={top_p}, min_p={min_p}")
            
            # Test each combination multiple times
            combination_results = []
            for _ in range(num_samples):
                for question in self.test_questions:
                    # Format prompt with ChatML
                    messages = []
                    if self.system_prompt:
                        messages.append({"role": "system", "content": self.system_prompt})
                    messages.append({"role": "user", "content": question})
                    
                    formatted_prompt = self.tokenizer.apply_chat_template(
                        messages,
                        tokenize=False
                    )
                    
                    # Generate response
                    response = ""
                    for token in stream_generate(
                        self.model,
                        self.tokenizer,
                        formatted_prompt,
                        temp=temp,
                        top_p=top_p,
                        min_p=min_p
                    ):
                        response += token.text
                        
                        # Stop if response gets too long
                        if len(response) > 500:
                            break
                    
                    # Evaluate response
                    scores = self.evaluate_response(response)
                    combination_results.append({
                        "question": question,
                        "response": response,
                        "scores": scores
                    })
            
            # Calculate average scores for this combination
            avg_scores = {}
            for metric in combination_results[0]["scores"].keys():
                avg_scores[metric] = np.mean([r["scores"][metric] for r in combination_results])
            
            results.append({
                "parameters": {
                    "temp": temp,
                    "top_p": top_p,
                    "min_p": min_p
                },
                "average_scores": avg_scores,
                "examples": combination_results
            })
            
            # Save results after each combination
            self.save_results(results)
        
        return results
    
    def save_results(self, results: List[Dict]):
        """Save results to file."""
        with open(self.output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved results to {self.output_file}")
    
    def get_best_parameters(self, results: List[Dict] = None) -> Dict:
        """
        Get the best performing parameters.
        
        Args:
            results: List of parameter search results. If None, load from file.
            
        Returns:
            Dictionary with best parameters and their scores
        """
        if results is None:
            with open(self.output_file) as f:
                results = json.load(f)
        
        # Sort by total score
        sorted_results = sorted(
            results,
            key=lambda x: x["average_scores"]["total_score"],
            reverse=True
        )
        
        best = sorted_results[0]
        print("\nBest parameters found:")
        print(json.dumps(best["parameters"], indent=2))
        print("\nScores:")
        print(json.dumps(best["average_scores"], indent=2))
        
        return best

def main():
    # Example usage
    optimizer = MLXParamOptimizer(
        model_path="mlx-community/Hermes-2-Pro-Llama-3-8B-4bit",
        adapter_path="adapters",
        test_questions=[
            "What is your opinion on this topic?",
            "How would you explain this concept?",
            "What are the main considerations here?"
        ],
        system_prompt="You are a helpful assistant."
    )
    
    # Custom parameter ranges to test
    param_ranges = {
        'temp': [0.7, 0.8, 0.9],
        'top_p': [0.92, 0.95],
        'min_p': [0.05, 0.08]
    }
    
    # Run parameter search
    results = optimizer.test_parameters(param_ranges)
    
    # Get best parameters
    best = optimizer.get_best_parameters(results)
    
    print("\nParameter search complete!")
    print(f"Best configuration saved to {optimizer.output_file}")

if __name__ == "__main__":
    main() 