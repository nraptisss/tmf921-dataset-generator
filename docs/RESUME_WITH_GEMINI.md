# Quick guide to resume experiments with Gemini API

## ✅ Good News!

Your system already supports Gemini API (Google's free LLM)!  
No need to install anything new.

## 🚀 Resume Experiments with Gemini

### Option 1: Update Experiment Script (Recommended)

Just update the experiments to use Gemini instead of Groq:

```python
# Edit: d:\dataset\experiments\run_experiments.py

# Line 60 - Update baseline:
llm = LLMInterface(provider="gemini")  # Changed from "groq"

# Line 140 - Update RAG:
translator = RAGTranslator(
    llm_provider="gemini",  # Changed from "groq"
    retrieval_strategy=strategy,
    k=k
)
```

### Option 2: Quick Gemini Test

Test that Gemini works first:

```bash
# Make sure you have Gemini API key in .env
python -c "from llm_interface import LLMInterface; llm = LLMInterface('gemini'); print(llm.generate('You are helpful', 'Say hello', temperature=0.5))"
```

## 📝 Get Gemini API Key (if needed)

1. Go to: https://aistudio.google.com/apikey
2. Click "Create API Key"
3. Copy the key
4. Add to `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```

## ⚡ Gemini vs Groq

| Feature | Groq | Gemini |
|---------|------|--------|
| Free Tier | 100k tokens/day | 1,500 requests/day |
| Model | llama-3.3-70b | gemini-1.5-flash |
| Speed | Very fast | Fast |
| Status | Hit limit ❌ | Available ✅ |

**For 83 test intents × 4 experiments = 332 requests**  
✅ Gemini: No problem!

## 🎯 Resume Your Experiments

```bash
# After updating the script:
python experiments/run_experiments.py
```

That's it! No new setup needed. 🚀
