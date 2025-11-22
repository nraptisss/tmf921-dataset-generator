"""
TMF921 Intent Translation Experiments
Compare Baseline vs RAG approaches
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from core.intent_translator import IntentTranslator
from rag.rag_translator import RAGTranslator
from core.validator import TMF921Validator
from tqdm import tqdm


class ExperimentRunner:
    """Run and compare different translation approaches"""
    
    def __init__(self, test_data_path: str = 'data/processed/test_intents.json'):
        """
        Initialize experiment runner
        
        Args:
            test_data_path: Path to test dataset
        """
        self.test_data_path = test_data_path
        self.test_data = self.load_test_data()
        self.validator = TMF921Validator()
        self.results = {}
        
        print(f"Loaded {len(self.test_data)} test intents")
    
    def load_test_data(self) -> List[Dict]:
        """Load test dataset"""
        with open(self.test_data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def run_baseline(self, max_intents: int = None) -> Dict[str, Any]:
        """
        Run baseline experiment (direct translation)
        
        Args:
            max_intents: Maximum number of intents to test (None = all)
        
        Returns:
            Experiment results
        """
        print("\n" + "=" * 70)
        print("EXPERIMENT: BASELINE (Direct Translation)")
        print("=" * 70)
        
        from core.llm_interface import LLMInterface
        llm = LLMInterface(provider="groq")
        translator = IntentTranslator(llm=llm)
        
        test_subset = self.test_data[:max_intents] if max_intents else self.test_data
        results = []
        
        start_time = time.time()
        
        for item in tqdm(test_subset, desc="Translating"):
            user_intent = item['user_intent']
            reference = item['tmf921_intent']
            
            try:
                # Translate
                generated = translator.translate(user_intent)
                
                # Validate
                validation = self.validator.validate_intent(generated)
                
                results.append({
                    'user_intent': user_intent,
                    'generated': generated,
                    'reference': reference,
                    'valid': validation['valid'],
                    'errors': validation.get('errors', [])
                })
            
            except Exception as e:
                results.append({
                    'user_intent': user_intent,
                    'generated': None,
                    'reference': reference,
                    'valid': False,
                    'errors': [str(e)]
                })
        
        elapsed_time = time.time() - start_time
        
        # Calculate metrics
        metrics = self.calculate_metrics(results, elapsed_time)
        
        return {
            'experiment': 'baseline',
            'config': {'provider': 'groq', 'model': 'llama-3.3-70b'},
            'results': results,
            'metrics': metrics
        }
    
    def run_rag_experiment(
        self,
        strategy: str = 'topk',
        k: int = 5,
        max_intents: int = None
    ) -> Dict[str, Any]:
        """
        Run RAG experiment
        
        Args:
            strategy: Retrieval strategy (topk, mmr, hybrid)
            k: Number of examples to retrieve
            max_intents: Maximum number of intents to test
        
        Returns:
            Experiment results
        """
        print("\n" + "=" * 70)
        print(f"EXPERIMENT: RAG ({strategy.upper()}, k={k})")
        print("=" * 70)
        
        translator = RAGTranslator(
            llm_provider="groq",
            retrieval_strategy=strategy,
            k=k
        )
        
        test_subset = self.test_data[:max_intents] if max_intents else self.test_data
        results = []
        
        start_time = time.time()
        
        for item in tqdm(test_subset, desc="Translating"):
            user_intent = item['user_intent']
            reference = item['tmf921_intent']
            
            try:
                # Translate with RAG
                generated = translator.translate(user_intent)
                
                # Validate
                validation = self.validator.validate_intent(generated)
                
                results.append({
                    'user_intent': user_intent,
                    'generated': generated,
                    'reference': reference,
                    'valid': validation['valid'],
                    'errors': validation.get('errors', [])
                })
            
            except Exception as e:
                results.append({
                    'user_intent': user_intent,
                    'generated': None,
                    'reference': reference,
                    'valid': False,
                    'errors': [str(e)]
                })
        
        elapsed_time = time.time() - start_time
        
        # Calculate metrics
        metrics = self.calculate_metrics(results, elapsed_time)
        
        return {
            'experiment': f'rag_{strategy}_k{k}',
            'config': {
                'provider': 'groq',
                'model': 'llama-3.3-70b',
                'strategy': strategy,
                'k': k
            },
            'results': results,
            'metrics': metrics
        }
    
    def calculate_metrics(self, results: List[Dict], elapsed_time: float) -> Dict:
        """Calculate experiment metrics"""
        total = len(results)
        valid = sum(1 for r in results if r['valid'])
        invalid = total - valid
        
        return {
            'total_intents': total,
            'valid_intents': valid,
            'invalid_intents': invalid,
            'success_rate': (valid / total * 100) if total > 0 else 0,
            'total_time_seconds': elapsed_time,
            'avg_time_per_intent': elapsed_time / total if total > 0 else 0
        }
    
    def compare_experiments(self, experiments: List[Dict]) -> Dict:
        """Compare multiple experiments"""
        comparison = {
            'summary': [],
            'best_approach': None,
            'timestamp': datetime.now().isoformat()
        }
        
        for exp in experiments:
            comparison['summary'].append({
                'experiment': exp['experiment'],
                'config': exp['config'],
                'metrics': exp['metrics']
            })
        
        # Find best approach (highest success rate)
        best = max(experiments, key=lambda x: x['metrics']['success_rate'])
        comparison['best_approach'] = best['experiment']
        
        return comparison
    
    def save_results(self, experiments: List[Dict], output_dir: str = 'experiments/results'):
        """Save experiment results"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save individual experiments
        for exp in experiments:
            filename = f"{exp['experiment']}_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(exp, f, indent=2, ensure_ascii=False)
            
            print(f"Saved: {filepath}")
        
        # Save comparison
        comparison = self.compare_experiments(experiments)
        comparison_file = os.path.join(output_dir, f'comparison_{timestamp}.json')
        
        with open(comparison_file, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)
        
        print(f"Saved comparison: {comparison_file}")
        
        return comparison
    
    def print_comparison(self, comparison: Dict):
        """Print comparison results"""
        print("\n" + "=" * 70)
        print("EXPERIMENT COMPARISON RESULTS")
        print("=" * 70)
        
        # Header
        print(f"\n{'Experiment':<25} {'Success Rate':<15} {'Avg Time (s)':<15}")
        print("-" * 70)
        
        # Results
        for summary in comparison['summary']:
            exp_name = summary['experiment']
            success_rate = summary['metrics']['success_rate']
            avg_time = summary['metrics']['avg_time_per_intent']
            
            print(f"{exp_name:<25} {success_rate:>6.2f}%        {avg_time:>6.3f}s")
        
        print("-" * 70)
        print(f"\nBest Approach: {comparison['best_approach']}")
        print("=" * 70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Run TMF921 translation experiments')
    parser.add_argument(
        '--experiments',
        nargs='+',
        default=['baseline', 'rag_topk3', 'rag_topk5', 'rag_mmr5'],
        help='Experiments to run'
    )
    parser.add_argument(
        '--max-intents',
        type=int,
        default=None,
        help='Maximum number of test intents (default: all 83)'
    )
    parser.add_argument(
        '--output-dir',
        default='experiments/results',
        help='Output directory for results'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("TMF921 INTENT TRANSLATION EXPERIMENTS")
    print("=" * 70)
    print(f"Test intents: {args.max_intents or 'all (83)'}")
    print(f"Experiments: {', '.join(args.experiments)}")
    print("=" * 70)
    
    # Initialize runner
    runner = ExperimentRunner()
    
    # Run experiments
    all_experiments = []
    
    for exp_name in args.experiments:
        if exp_name == 'baseline':
            result = runner.run_baseline(max_intents=args.max_intents)
            all_experiments.append(result)
        
        elif exp_name.startswith('rag_'):
            # Parse: rag_topk3, rag_mmr5, etc.
            parts = exp_name.replace('rag_', '').split('_')
            
            # Extract strategy and k
            if parts[0].startswith('topk'):
                strategy = 'topk'
                k = int(parts[0][4:]) if len(parts[0]) > 4 else 5
            elif parts[0].startswith('mmr'):
                strategy = 'mmr'
                k = int(parts[0][3:]) if len(parts[0]) > 3 else 5
            elif parts[0].startswith('hyb'):
                strategy = 'hybrid'
                k = int(parts[0][6:]) if len(parts[0]) > 6 else 5
            else:
                strategy = 'topk'
                k = 5
            
            result = runner.run_rag_experiment(
                strategy=strategy,
                k=k,
                max_intents=args.max_intents
            )
            all_experiments.append(result)
    
    # Save and compare results
    comparison = runner.save_results(all_experiments, output_dir=args.output_dir)
    runner.print_comparison(comparison)
    
    print(f"\n[OK] Experiments complete! Results saved to {args.output_dir}/")


if __name__ == "__main__":
    main()
