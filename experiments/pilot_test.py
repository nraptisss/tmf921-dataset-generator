"""
Quick pilot test - Run 10 intents to verify everything works
"""
import subprocess
import sys

def main():
    print("=" * 70)
    print("PILOT TEST: Running 10 test intents")
    print("=" * 70)
    print("\nThis will test:")
    print("  1. Baseline (direct translation)")
    print("  2. RAG Top-K (k=3)")
    print("  3. RAG Top-K (k=5)")
    print("  4. RAG MMR (k=5)")
    print("\nEstimated time: ~3-5 minutes")
    print("=" * 70)
    
    # Run pilot
    cmd = [
        sys.executable,
        "experiments/run_experiments.py",
        "--max-intents", "10",
        "--experiments", "baseline", "rag_topk3", "rag_topk5", "rag_mmr5"
    ]
    
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
