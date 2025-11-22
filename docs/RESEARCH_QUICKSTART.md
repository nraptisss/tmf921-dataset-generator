# TMF921 Research Quick Start

## 🚀 Run Experiments (One Command Each)

### Quick Test (10 intents, ~2 min)
```bash
python run.py --pilot
```

### Full Experiments (83 intents, ~30 min)
```bash
python run.py --full
```

### Single Baseline Test
```bash
python run.py --baseline-only
```

### Single RAG Test
```bash
python run.py --rag-only
```

---

## 📊 View Results

### Latest Results
```bash
python run.py --show-results
```

### Compare All Experiments
```bash
python run.py --compare
```

---

## 🔧 Quick Tests

### Test Single Intent
```bash
python test.py "Create emergency network for hospital"
```

### Test RAG Retrieval
```bash
python test.py --retrieval "IoT sensor network"
```

### Test Vector Database
```bash
python test.py --database
```

---

## � Project Structure

```
d:\dataset\
├── run.py              # Main runner (all experiments)
├── test.py             # Quick testing
├── experiments/        # Results & comparison
├── data/              # Train/val/test splits
└── vector_db/         # RAG database
```

---

## ⚡ Quick Commands Summary

| Command | What It Does | Time |
|---------|-------------|------|
| `python run.py --pilot` | Test with 10 intents | 2 min |
| `python run.py --full` | Full experiments | 30 min |
| `python test.py "text"` | Test one intent | 5 sec |
| `python run.py --show-results` | View latest results | instant |

**That's it!** Simple and fast for research iteration.
