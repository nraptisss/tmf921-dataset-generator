# Directory Reorganization Plan

## New Structure

```
d:\dataset\
├── README.md                 # Main project readme
├── run.py                    # Quick experiment runner
├── test.py                   # Quick testing utility
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── .gitignore               # Git ignore rules
│
├── docs/                     # All documentation
│   ├── RESEARCH_QUICKSTART.md
│   ├── QUICK_COMMANDS.md
│   ├── SETUP_GUIDE.md
│   ├── RAG_SETUP.md
│   ├── CODE_QUALITY_REPORT.md
│   └── HUGGINGFACE_SETUP.md
│
├── src/                      # Source code
│   ├── core/                 # Core modules
│   │   ├── __init__.py
│   │   ├── llm_interface.py
│   │   ├── intent_translator.py
│   │   ├── intent_categorizer.py
│   │   ├── tmf921_templates.py
│   │   └── validator.py
│   ├── rag/                  # RAG system
│   │   ├── __init__.py
│   │   ├── build_vector_db.py
│   │   ├── rag_retriever.py
│   │   └── rag_translator.py
│   └── scripts/              # Utility scripts
│       ├── __init__.py
│       ├── generate_dataset.py
│       └── split_dataset.py
│
├── experiments/              # Experiment framework
│   ├── run_experiments.py
│   ├── pilot_test.py
│   └── results/             # Experiment outputs
│
├── data/                     # Datasets
│   ├── raw/
│   │   └── telecom_intents.json
│   ├── processed/
│   │   ├── train_intents.json
│   │   ├── val_intents.json
│   │   └── test_intents.json
│   └── output/
│       └── tmf921_dataset.json
│
├── resources/                # Reference materials
│   ├── specifications/
│   │   ├── TMF921_Intent_Management_v5.0.0_specification.pdf
│   │   └── All_PDFs/
│   └── examples/            # TMF921 examples
│       └── intent-driven IDAN3-TMF921 main ontologies/
│
├── vector_db/                # ChromaDB storage
│
└── research/                 # Research notes
    └── FREE_STACK_GUIDE.md
```

## Benefits

1. **Clean Root**: Only essential files
2. **Organized Docs**: All documentation in one place
3. **Clear Source**: Proper src/ structure with packages
4. **Separated Data**: Raw, processed, output clearly separated
5. **Resources**: Reference materials isolated
6. **Professional**: Standard Python project layout

## Migration Steps

1. Create new directory structure
2. Move files to appropriate locations
3. Update import statements
4. Update file paths in scripts
5. Test all functionality
