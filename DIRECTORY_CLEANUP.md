# Directory Cleanup Recommendations

## Issues Identified

### 1. Duplicate Python Files in Root ❌
These files exist in BOTH root and `src/` (from the Git merge):
- `generate_dataset.py`
- `intent_categorizer.py`
- `intent_translator.py`
- `llm_interface.py`
- `tmf921_templates.py`
- `validator.py`

**Solution**: Delete from root, keep in `src/`

### 2. Misplaced Data Files ❌
- `telecom_intents.json` → should be in `data/raw/`
- `tmf921_intents.json` → should be in `data/output/`

### 3. Duplicate examples/ Directory ❌
- Root `examples/` → should merge into `resources/examples/`

### 4. Temporary Files ❌
- `GIT_CONFIG_NEEDED.md` (task complete, can delete)
- `RESOLVE_CONFLICTS.md` (task complete, can delete)
- `SETUP_GUIDE.md` (duplicate, already in `docs/`)

---

## Quick Fix Commands

```bash
# Remove duplicate Python files from root
Remove-Item -Path "generate_dataset.py", "intent_categorizer.py", "intent_translator.py", "llm_interface.py", "tmf921_templates.py", "validator.py" -Force

# Move data files to proper locations
Move-Item -Path "telecom_intents.json" -Destination "data\raw\" -Force
Move-Item -Path "tmf921_intents.json" -Destination "data\output\" -Force

# Merge examples and remove duplicate
Move-Item -Path "examples\*" -Destination "resources\examples\" -Force
Remove-Item -Path "examples" -Recurse -Force

# Remove temporary files
Remove-Item -Path "GIT_CONFIG_NEEDED.md", "RESOLVE_CONFLICTS.md" -Force

# Move SETUP_GUIDE to docs (it's a duplicate but merge it)
Move-Item -Path "SETUP_GUIDE.md" -Destination "docs\" -Force
```

---

## After Cleanup - Ideal Structure

```
d:\dataset\
├── .env, .gitignore, LICENSE, README.md, requirements.txt
├── run.py, test.py                    # Quick utilities
├── docs/                              # All documentation
├── src/
│   ├── core/                         # Core modules
│   ├── rag/                          # RAG system
│   └── scripts/                      # Utility scripts
├── experiments/                       # Experiment framework
├── data/
│   ├── raw/telecom_intents.json     # Source data
│   ├── processed/                    # Train/val/test
│   └── output/tmf921_intents.json   # Generated
├── resources/
│   ├── specifications/               # PDFs
│   └── examples/                     # All examples
└── vector_db/                        # ChromaDB
```

**Result**: Clean root with only essential files!

---

**Run the commands above to fix!** ✅
