"""
TMF921 Dataset Generator
Main script to generate the complete dataset of user intent to TMF921 intent pairings
"""

import json
import logging
import os
from datetime import datetime
from typing import List, Dict
from pathlib import Path
from tqdm import tqdm
import time

from llm_interface import LLMInterface
from intent_translator import IntentTranslator


class DatasetGenerator:
    """Generates TMF921 intent dataset from natural language intents"""
    
    def __init__(self, provider: str = "groq"):
        """
        Initialize the dataset generator
        
        Args:
            provider: LLM provider to use
        """
        self.provider = provider
        self.llm = None
        self.translator = None
        self.output_dir = Path("output")
        self.checkpoint_dir = self.output_dir / "checkpoints"
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self._initialize()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = self.output_dir / "generation_log.txt"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _initialize(self):
        """Initialize LLM and translator"""
        self.logger.info(f"Initializing with provider:  {self.provider}")
        self.llm = LLMInterface(provider=self.provider)
        self.translator = IntentTranslator(self.llm)
        self.logger.info("✓ Initialization complete")
    
    def load_user_intents(self, filepath: str = "telecom_intents.json") -> List[str]:
        """
        Load user intents from JSON file
        
        Args:
            filepath: Path to intents file
        
        Returns:
            List of intent strings
        """
        self.logger.info(f"Loading intents from: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            intents = json.load(f)
        
        self.logger.info(f"✓ Loaded {len(intents)} intents")
        return intents
    
    def load_checkpoint(self) -> Dict:
        """Load the latest checkpoint if it exists"""
        checkpoints = list(self.checkpoint_dir.glob("checkpoint_*.json"))
        
        if not checkpoints:
            return None
        
        # Get the latest checkpoint
        latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
        
        self.logger.info(f"Loading checkpoint: {latest.name}")
        
        with open(latest, 'r', encoding='utf-8') as f:
            checkpoint_data = json.load(f)
        
        return checkpoint_data
    
    def save_checkpoint(self, dataset: Dict, index: int):
        """Save a checkpoint"""
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{index}.json"
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2)
        
        self.logger.info(f"✓ Checkpoint saved at index {index}")
    
    def generate_dataset(self, 
                        start_index: int = 0, 
                        max_intents: int = None,
                        checkpoint_interval: int = 50) -> Dict:
        """
        Generate the complete TMF921 dataset
        
        Args:
            start_index: Index to start from (for resuming)
            max_intents: Maximum number of intents to process (None = all)
            checkpoint_interval: Save checkpoint every N intents
        
        Returns:
            Complete dataset dictionary
        """
        # Load user intents
        user_intents = self.load_user_intents()
        
        # Determine range
        end_index = len(user_intents) if max_intents is None else min(start_index + max_intents, len(user_intents))
        total_to_process = end_index - start_index
        
        self.logger.info(f"Processing intents {start_index} to {end_index} ({total_to_process} total)")
        
        # Initialize dataset structure
        dataset = {
            "dataset_metadata": {
                "generation_date": datetime.utcnow().isoformat() + "Z",
                "total_intents": total_to_process,
                "successful": 0,
                "failed": 0,
                "model_used": f"{self.provider}:{self.llm.model}",
                "version": "1.0.0",
                "start_index": start_index,
                "end_index": end_index
            },
            "intent_pairs": []
        }
        
        # Load checkpoint if resuming
        checkpoint = self.load_checkpoint()
        if checkpoint and start_index > 0:
            self.logger.info("Resuming from checkpoint...")
            dataset = checkpoint
        
        # Process intents with progress bar
        failed_intents = []
        
        with tqdm(total=total_to_process, desc="Generating TMF921 intents", unit="intent") as pbar:
            for idx in range(start_index, end_index):
                user_intent = user_intents[idx]
                
                try:
                    # Translate intent
                    start_time = time.time()
                    tmf921_intent = self.translator.translate(user_intent, intent_index=idx + 1)
                    generation_time = time.time() - start_time
                    
                    # Create pair entry
                    pair = {
                        "id": idx + 1,
                        "user_intent": user_intent,
                        "tmf921_intent": tmf921_intent,
                        "generation_timestamp": datetime.utcnow().isoformat() + "Z",
                        "validation_status": "valid",  # Will be updated by validator
                        "metadata": {
                            "generation_time_seconds": round(generation_time, 2),
                            "retry_count": 0
                        }
                    }
                    
                    dataset["intent_pairs"].append(pair)
                    dataset["dataset_metadata"]["successful"] += 1
                    
                    pbar.set_postfix({"success": dataset["dataset_metadata"]["successful"], 
                                     "failed": dataset["dataset_metadata"]["failed"]})
                    
                except Exception as e:
                    self.logger.error(f"Failed to process intent {idx + 1}: {str(e)}")
                    dataset["dataset_metadata"]["failed"] += 1
                    failed_intents.append({
                        "id": idx + 1,
                        "user_intent": user_intent,
                        "error": str(e)
                    })
                
                # Update progress bar
                pbar.update(1)
                
                # Save checkpoint
                if (idx + 1) % checkpoint_interval == 0:
                    self.save_checkpoint(dataset, idx + 1)
                
                # Small delay to respect rate limits (Groq is very fast so minimal delay)
                time.sleep(0.1)
        
        # Save failed intents
        if failed_intents:
            failed_file = self.output_dir / "failed_intents.json"
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump(failed_intents, f, indent=2)
            self.logger.warning(f"Saved {len(failed_intents)} failed intents to: {failed_file}")
        
        # Update final metadata
        dataset["dataset_metadata"]["completion_date"] = datetime.utcnow().isoformat() + "Z"
        dataset["dataset_metadata"]["total_intents"] = len(dataset["intent_pairs"])
        
        return dataset
    
    def save_dataset(self, dataset: Dict, filename: str = "tmf921_dataset.json"):
        """Save the final dataset"""
        output_file = self.output_dir / filename
        
        self.logger.info(f"Saving dataset to: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2)
        
        self.logger.info(f"✓ Dataset saved successfully")
        
        # Print summary
        metadata = dataset["dataset_metadata"]
        self.logger.info("\n" + "=" * 60)
        self.logger.info("GENERATION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Intents Processed: {metadata['total_intents']}")
        self.logger.info(f"Successful: {metadata['successful']}")
        self.logger.info(f"Failed: {metadata['failed']}")
        self.logger.info(f"Success Rate: {metadata['successful'] / metadata['total_intents'] * 100:.1f}%")
        self.logger.info(f"Model Used: {metadata['model_used']}")
        self.logger.info(f"Output File: {output_file}")
        self.logger.info("=" * 60)
        
        # Token usage stats
        token_stats = self.llm.get_token_stats()
        if token_stats["total"] > 0:
            self.logger.info("\nToken Usage:")
            self.logger.info(f"  Prompt Tokens: {token_stats['prompt']:,}")
            self.logger.info(f"  Completion Tokens: {token_stats['completion']:,}")
            self.logger.info(f"  Total Tokens: {token_stats['total']:,}")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate TMF921 Intent Dataset")
    parser.add_argument("--provider", type=str, default="groq", 
                       choices=["groq", "gemini", "together"],
                       help="LLM provider to use")
    parser.add_argument("--start", type=int, default=0,
                       help="Start index (for resuming)")
    parser.add_argument("--max", type=int, default=None,
                       help="Maximum intents to process (for testing)")
    parser.add_argument("--checkpoint-interval", type=int, default=50,
                       help="Save checkpoint every N intents")
    
    args = parser.parse_args()
    
    # Check for API key
    if args.provider == "groq" and not os.getenv("GROQ_API_KEY"):
        print("\n⚠ ERROR: GROQ_API_KEY not found in environment")
        print("Please create a .env file with your Groq API key:")
        print("  GROQ_API_KEY=your_key_here")
        print("\nGet your free key at: https://console.groq.com/")
        return
    
    print("\n" + "=" * 60)
    print("TMF921 DATASET GENERATOR")
    print("=" * 60)
    print(f"Provider: {args.provider}")
    print(f"Start Index: {args.start}")
    print(f"Max Intents: {args.max if args.max else 'All'}")
    print("=" * 60 + "\n")
    
    try:
        # Initialize generator
        generator = DatasetGenerator(provider=args.provider)
        
        # Generate dataset
        dataset = generator.generate_dataset(
            start_index=args.start,
            max_intents=args.max,
            checkpoint_interval=args.checkpoint_interval
        )
        
        # Save final dataset
        generator.save_dataset(dataset)
        
        print("\n✓ Dataset generation complete!")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Generation interrupted by user")
        print("Progress has been checkpointed. You can resume with --start option.")
    
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
