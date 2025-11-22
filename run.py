"""
Main Research Runner
Quick access to all experiments
"""

import sys
import argparse
import subprocess
from pathlib import Path

def run_pilot():
    """Run pilot test (10 intents)"""
    print("[RUN] Running pilot test (10 intents)...")
    subprocess.run([sys.executable, "experiments/pilot_test.py"])

def run_full():
    """Run full experiments (83 intents)"""
    print("[RUN] Running full experiments (83 intents)...")
    subprocess.run([sys.executable, "experiments/run_experiments.py"])

def run_baseline_only():
    """Run only baseline experiment"""
    print("[RUN] Running baseline only...")
    subprocess.run([
        sys.executable,
        "experiments/run_experiments.py",
        "--experiments", "baseline"
    ])

def run_rag_only(strategy="topk", k=5):
    """Run only RAG experiment"""
    print(f"[RUN] Running RAG only ({strategy}, k={k})...")
    subprocess.run([
        sys.executable,
        "experiments/run_experiments.py",
        "--experiments", f"rag_{strategy}{k}"
    ])

def show_results():
    """Show latest results"""
    import json
    import glob
    
    results_dir = Path("experiments/results")
    comparison_files = sorted(results_dir.glob("comparison_*.json"))
    
    if not comparison_files:
        print("[ERROR] No results found. Run experiments first!")
        return
    
    latest = comparison_files[-1]
    print(f"\n[RESULTS] Latest Results: {latest.name}\n")
    
    with open(latest) as f:
        data = json.load(f)
    
    print(f"{'Experiment':<25} {'Success Rate':<15} {'Avg Time':<15}")
    print("-" * 70)
    
    for summary in data['summary']:
        name = summary['experiment']
        success = summary['metrics']['success_rate']
        time = summary['metrics']['avg_time_per_intent']
        print(f"{name:<25} {success:>6.2f}%        {time:>6.3f}s")
    
    print("-" * 70)
    print(f"\n[OK] Best: {data['best_approach']}")

def compare_all():
    """Compare all experiment runs"""
    import json
    from pathlib import Path
    
    results_dir = Path("experiments/results")
    comparison_files = sorted(results_dir.glob("comparison_*.json"))
    
    if not comparison_files:
        print("[ERROR] No results found!")
        return
    
    print(f"\n[RESULTS] All Experiment Runs ({len(comparison_files)} total)\n")
    
    for comp_file in comparison_files:
        with open(comp_file) as f:
            data = json.load(f)
        
        print(f"\n{comp_file.name}:")
        print(f"  Best: {data['best_approach']}")
        for s in data['summary']:
            print(f"  - {s['experiment']}: {s['metrics']['success_rate']:.1f}%")

def main():
    parser = argparse.ArgumentParser(description='TMF921 Research Runner')
    parser.add_argument('--pilot', action='store_true', help='Run pilot test (10 intents)')
    parser.add_argument('--full', action='store_true', help='Run full experiments')
    parser.add_argument('--baseline-only', action='store_true', help='Run baseline only')
    parser.add_argument('--rag-only', action='store_true', help='Run RAG only')
    parser.add_argument('--show-results', action='store_true', help='Show latest results')
    parser.add_argument('--compare', action='store_true', help='Compare all runs')
    
    args = parser.parse_args()
    
    if args.pilot:
        run_pilot()
    elif args.full:
        run_full()
    elif args.baseline_only:
        run_baseline_only()
    elif args.rag_only:
        run_rag_only()
    elif args.show_results:
        show_results()
    elif args.compare:
        compare_all()
    else:
        # Show help if no args
        parser.print_help()
        print("\nQuick start:")
        print("  python run.py --pilot          # Test with 10 intents")
        print("  python run.py --show-results   # View latest results")

if __name__ == "__main__":
    main()
