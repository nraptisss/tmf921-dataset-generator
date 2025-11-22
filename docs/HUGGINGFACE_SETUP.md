# HuggingFace Setup Guide

## 🚀 Quick Setup (2 minutes!)

### 1. Get Free API Key

1. Go to: **https://huggingface.co/settings/tokens**
2. Click **"New Token"**
3. Give it a name (e.g., "tmf921-experiments")
4. Select **"Read"** access
5. Click **"Generate"**
6. Copy the token

### 2. Add to .env File

Open `d:\dataset\.env` and add:

```
HUGGINGFACE_API_KEY=hf_your_token_here
```

### 3. Install Package

```bash
pip install huggingface_hub
```

### 4. Run Experiments!

```bash
python experiments/pilot_test.py
```

---

## ✅ Why HuggingFace?

- ✅ **Free tier**: 1,000 requests/hour
- ✅ **No daily limits** like Groq
- ✅ **Good models**: Mistral-7B-Instruct
- ✅ **Fast** enough for experiments
- ✅ **Easy** to set up

---

## 📊 Expected Performance

Using **Mistral-7B-Instruct-v0.3**:
- Quality: Good (slightly lower than Llama-70B but still excellent)
- Speed: ~2-4s per intent
- Limit: 1,000 requests/hour (plenty!)
- Cost: **$0**

**For your 332 total requests**: No problem! ✅

---

**Ready in 2 minutes!** Get your token and let's go! 🚀
