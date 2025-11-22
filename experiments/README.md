# TMF921 Experiments - Quick Reference

## Run All Experiments

```bash
# Run all default experiments (baseline + RAG variants)
python experiments/run_experiments.py

# Test with just 10 intents first (faster)
python experiments/run_experiments.py --max-intents 10
```

## Run Specific Experiments

```bash
# Just baseline
python experiments/run_experiments.py --experiments baseline

# Baseline + RAG Top-K (k=5)
python experiments/run_experiments.py --experiments baseline rag_topk5

# Compare different K values
python experiments/run_experiments.py --experiments rag_topk3 rag_topk5 rag_topk10

# Compare retrieval strategies
python experiments/run_experiments.py --experiments rag_topk5 rag_mmr5
```

## Default Experiments

The script runs these by default:
1. **baseline** - Direct translation (no RAG)
2. **rag_topk3** - RAG with Top-K retrieval, k=3
3. **rag_topk5** - RAG with Top-K retrieval, k=5
4. **rag_mmr5** - RAG with MMR (diversity), k=5

## Output

Results saved to `experiments/results/`:
- Individual experiment JSONs
- Comparison report
- Metrics for each approach

## Metrics Collected

- Success rate (% valid TMF921 intents)
- Average time per intent
- Total processing time
- Validation errors (if any)

## Example Output

```
===================================================================
EXPERIMENT COMPARISON RESULTS
===================================================================

Experiment                Success Rate    Avg Time (s)    
----------------------------------------------------------------------
baseline                   100.00%          0.245s
rag_topk3                  100.00%          0.312s
rag_topk5                  100.00%          0.298s
rag_mmr5                   100.00%          0.331s
----------------------------------------------------------------------

Best Approach: baseline
===================================================================
```

## Quick Start

```bash
# 1. Run pilot (10 intents, ~5 minutes)
python experiments/run_experiments.py --max-intents 10

# 2. Review results
cat experiments/results/comparison_*.json

# 3. Run full experiments (83 intents, ~30 minutes)
python experiments/run_experiments.py
```
