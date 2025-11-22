# Quick Test Commands

## 🚀 Run Everything

```bash
# Pilot test (fast)
python run.py --pilot

# Full experiments
python run.py --full
```

## 🧪 Test Components

```bash
# Test LLM
python test.py --llm

# Test database
python test.py --database

# Test retrieval
python test.py --retrieval "emergency network"

# Test single intent
python test.py "Create 5G network slice"

# Test with RAG
python test.py "Create 5G network slice" --rag
```

## 📊 View Results

```bash
# Latest results
python run.py --show-results

# Compare all runs
python run.py --compare
```

## ⚡ Common Workflows

### Before Running Experiments
```bash
# Verify everything works
python test.py --llm
python test.py --database
```

### Quick Iteration
```bash
# Test one intent (5 sec)
python test.py "Your intent here"

# Test with RAG (10 sec)
python test.py "Your intent here" --rag

# Run pilot when ready (2 min)
python run.py --pilot
```

### After Experiments
```bash
# View results
python run.py --show-results

# Compare multiple runs
python run.py --compare
```

---

**That's it!** Everything in 1-2 commands.
