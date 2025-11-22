# TMF921 RAG Research System

🚀 **RAG-Enhanced TMF921 Intent Translation Research** - Comparing baseline vs. retrieval-augmented generation for translating natural language telecom intents into TMF921-compliant JSON structures.

[![TMF921](https://img.shields.io/badge/TMF921-v5.0.0-blue)](https://www.tmforum.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

This research project implements and evaluates a **Retrieval-Augmented Generation (RAG)** system for translating natural language telecom intents into TMF921 (Intent Management) compliant JSON structures with embedded Turtle RDF expressions.

### Research Question

**Does RAG improve the quality and consistency of LLM-generated TMF921 intents compared to baseline few-shot prompting?**

### Key Features

- 🔍 **RAG System**: Vector database with 663 training examples
- 📊 **Multiple Strategies**: Top-K, MMR, and Hybrid retrieval
- 🆚 **Baseline Comparison**: Direct translation without retrieval
- 🤖 **Free API Stack**: Groq (primary), Gemini, HuggingFace support
- ⚡ **Quick Testing**: `run.py` and `test.py` utilities
- 📈 **Experiment Framework**: Automated comparison and metrics

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API key (free at [console.groq.com](https://console.groq.com/))

### Installation

```bash
# Clone the repository
git clone https://github.com/nraptisss/tmf921-dataset-generator.git
cd tmf921-dataset-generator

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Quick Test

```bash
# Test database connection
python test.py --database

# Test LLM connection
python test.py --llm

# Test single intent translation
python test.py "Create a network slice for emergency services"
```

### Run Experiments

```bash
# Pilot test (10 intents)
python run.py --pilot

# Full experiments (83 test intents)
python run.py --full

# View results
python run.py --show-results
python run.py --compare
```

## 📁 Project Structure

```
tmf921-dataset-generator/
├── run.py                    # Quick experiment runner
├── test.py                   # Component testing utility
├── requirements.txt
├── README.md
│
├── docs/                     # Documentation (11 files)
│   ├── RESEARCH_QUICKSTART.md
│   ├── RAG_SETUP.md
│   ├── SETUP_GUIDE.md
│   └── ...
│
├── src/                      # Source code
│   ├── core/                 # Core modules
│   │   ├── llm_interface.py
│   │   ├── intent_translator.py
│   │   ├── tmf921_templates.py
│   │   ├── intent_categorizer.py
│   │   └── validator.py
│   ├── rag/                  # RAG system
│   │   ├── build_vector_db.py
│   │   ├── rag_retriever.py
│   │   └── rag_translator.py
│   └── scripts/              # Utility scripts
│       ├── generate_dataset.py
│       └── split_dataset.py
│
├── experiments/              # Experiment framework
│   ├── run_experiments.py
│   ├── pilot_test.py
│   └── results/
│
├── data/                     # Datasets
│   ├── raw/                  # telecom_intents.json (830)
│   ├── processed/            # train/val/test splits
│   │   ├── train_intents.json (663)
│   │   ├── val_intents.json   (83)
│   │   └── test_intents.json  (83)
│   └── output/               # Generated datasets
│
├── resources/                # Reference materials
│   ├── specifications/       # TMF921 PDFs
│   └── examples/             # TMF921 examples
│
└── vector_db/                # ChromaDB storage (663 vectors)
```

## 🔬 Research Methodology

### Dataset
- **830 telecom intents** covering diverse scenarios
- **80/10/10 split**: 663 train, 83 val, 83 test
- **Vector DB**: 663 training examples with sentence-transformers embeddings

### Experiments

1. **Baseline**: Direct translation (no retrieval)
2. **RAG Top-K (k=3)**: Retrieve 3 most similar examples
3. **RAG Top-K (k=5)**: Retrieve 5 most similar examples
4. **RAG MMR (k=5)**: Maximum Marginal Relevance for diversity

### Evaluation Metrics
- Semantic similarity to reference
- TMF921 compliance
- Turtle RDF validity
- Generation consistency

## 🔧 Configuration

### API Providers

**Groq** (Recommended)
```bash
python run.py --pilot
# Uses Groq by default
```

**Google Gemini**
```bash
# Update experiments/run_experiments.py
llm_provider="gemini"
```

**HuggingFace**
```bash
# See docs/HUGGINGFACE_SETUP.md
```

## 📊 Example Output

```json
{
  "id": 1,
  "user_intent": "Create a network slice for emergency ambulance communications",
  "tmf921_intent": {
    "name": "Intent_Emergency_Ambulance_1",
    "description": "...",
    "expression": {
      "@type": "TurtleExpression",
      "expressionValue": "@prefix icm: <...> ..."
    },
    "lifecycleStatus": "Created"
  },
  "validation_status": "valid"
}
```

## 📈 Experiment Results

Results are saved in `experiments/results/`:
- `baseline_YYYYMMDD_HHMMSS.json`
- `rag_topk_k3_YYYYMMDD_HHMMSS.json`
- `rag_topk_k5_YYYYMMDD_HHMMSS.json`
- `rag_mmr_k5_YYYYMMDD_HHMMSS.json`
- `comparison_YYYYMMDD_HHMMSS.json`

## 🎓 Use Cases

- RAG research for structured output generation
- TMF921 training data generation
- Baseline vs RAG comparisons
- Telecom intent modeling research
- TMF921 tooling development
- Few-shot learning benchmarks

## 📚 Documentation

- [Research Quickstart](docs/RESEARCH_QUICKSTART.md) - Start here!
- [RAG Setup Guide](docs/RAG_SETUP.md) - Vector DB setup
- [Quick Commands](docs/QUICK_COMMANDS.md) - Command reference
- [Setup Guide](docs/SETUP_GUIDE.md) - Detailed setup

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- TMForum for the TMF921 Intent Management specification
- Groq for providing ultra-fast free API access
- ChromaDB for vector storage
- Sentence Transformers for embeddings

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Research Focus**: RAG vs Baseline for TMF921 Generation  
**TMF921 Version**: v5.0.0  
**Stack**: 100% Free (Groq + ChromaDB + Sentence Transformers) ✨
