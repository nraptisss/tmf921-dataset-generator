# 100% Free Research Stack for TMF921 Intent Translation

> **Goal**: Run advanced RAG and agentic experiments with ZERO cost using free APIs and open-source tools.

---

## 🆓 Complete Free Stack

### 1. **LLM APIs** (All Free!)

#### **Primary: Groq API** ⭐ RECOMMENDED
```bash
# What you're already using!
API: https://console.groq.com/
Models: llama-3.1-70b-versatile, mixtral-8x7b-32768
Speed: 750 tokens/sec (FASTEST!)
Free Tier: 14,400 requests/day
Cost: $0
```

**Why Groq for Research**:
- ✅ Blazingly fast (2.5 min for 829 intents!)
- ✅ Large context window (32K tokens)
- ✅ State-of-the-art models (Llama 3.1 70B)
- ✅ No rate limits issues for research

#### **Alternative: Google Gemini**
```bash
API: https://aistudio.google.com/apikey
Models: gemini-1.5-flash, gemini-1.5-pro
Free Tier: 1,500 requests/day
Cost: $0
```

#### **Local Option: Ollama**
```bash
# Install Ollama
# Windows: https://ollama.com/download

# Pull models
ollama pull llama3.1:70b
ollama pull mistral

# Run locally - COMPLETELY FREE, NO INTERNET NEEDED
Cost: $0 (just electricity)
```

---

### 2. **Embeddings** (Free!)

#### **Option A: Sentence Transformers** ⭐ RECOMMENDED
```bash
pip install sentence-transformers

# Best models for semantic search
from sentence_transformers import SentenceTransformer

# Option 1: Balanced (recommended)
model = SentenceTransformer('all-mpnet-base-v2')
# 768 dimensions, 420M params

# Option 2: Larger, better quality
model = SentenceTransformer('all-MiniLM-L12-v2')
# 384 dimensions, faster

# Run locally - FREE
embeddings = model.encode(texts)
```

#### **Option B: Ollama Embeddings**
```bash
# Use Ollama for embeddings too
ollama pull nomic-embed-text

# Python API
import ollama
embeddings = ollama.embeddings(
    model='nomic-embed-text',
    prompt='your text here'
)
```

---

### 3. **Vector Database** (Free!)

#### **Option A: ChromaDB** ⭐ EASIEST
```bash
pip install chromadb

# Completely local, no server needed
import chromadb
client = chromadb.Client()

# Or persistent storage
client = chromadb.PersistentClient(path="./vector_db")

collection = client.create_collection("tmf921_intents")
collection.add(
    documents=texts,
    embeddings=embeddings,
    ids=ids
)

# Query
results = collection.query(
    query_texts=["new intent"],
    n_results=5
)
```

**Why ChromaDB**:
- ✅ Zero setup, works out of the box
- ✅ No server required
- ✅ Perfect for research/experiments
- ✅ Easy to share data with colleagues

#### **Option B: Qdrant (Local)**
```bash
pip install qdrant-client

# Run local Qdrant
from qdrant_client import QdrantClient
client = QdrantClient(":memory:")  # In-memory
# or
client = QdrantClient(path="./qdrant_db")  # Persistent

# More features than ChromaDB if needed
```

---

### 4. **Agentic Frameworks** (Free & Open-Source!)

#### **Option A: LangGraph** ⭐ RECOMMENDED FOR RESEARCH
```bash
pip install langgraph langchain-core

# Why LangGraph:
# - Built by LangChain team
# - Pure graph-based workflows
# - Easy to visualize agent interactions
# - Great for academic papers (cite-able!)
```

**Example Multi-Agent Workflow**:
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class TranslationState(TypedDict):
    user_intent: str
    analysis: dict
    retrieved_examples: list
    tmf921_intent: dict
    validation_result: dict

# Define agents as functions
def analyze_intent(state):
    # Call Groq to analyze
    analysis = groq_client.generate(
        f"Analyze this telecom intent: {state['user_intent']}"
    )
    return {"analysis": analysis}

def retrieve_examples(state):
    # Query ChromaDB
    results = collection.query(
        query_texts=[state['user_intent']],
        n_results=5
    )
    return {"retrieved_examples": results}

def generate_tmf921(state):
    # Call Groq with RAG context
    intent = groq_client.generate(
        prompt_with_rag_context(
            state['user_intent'],
            state['retrieved_examples']
        )
    )
    return {"tmf921_intent": intent}

def validate(state):
    # Your existing validator!
    result = validator.validate(state['tmf921_intent'])
    return {"validation_result": result}

# Build workflow graph
workflow = StateGraph(TranslationState)
workflow.add_node("analyze", analyze_intent)
workflow.add_node("retrieve", retrieve_examples)
workflow.add_node("generate", generate_tmf921)
workflow.add_node("validate", validate)

workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", "validate")
workflow.add_edge("validate", END)

app = workflow.compile()

# Run it!
result = app.invoke({"user_intent": "Create a network for..."})
```

#### **Option B: AutoGen**
```bash
pip install pyautogen

# Microsoft's multi-agent framework
# Good for conversational agents
```

#### **Option C: CrewAI**
```bash
pip install crewai

# More opinionated, task-oriented
# Good for specific workflows
```

---

## 💻 Complete Free Research Setup

### **Minimal Setup** (Start Here)
```bash
# 1. Python dependencies
pip install chromadb sentence-transformers langgraph groq google-generativeai

# 2. Get free API keys
# Groq: https://console.groq.com/
# Gemini: https://aistudio.google.com/apikey

# 3. Update .env
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key

# 4. Ready to go!
# Total cost: $0
# Total time: 5 minutes
```

### **Optional Local Setup** (No Internet Required)
```bash
# 1. Install Ollama
# Download from https://ollama.com/download

# 2. Pull models (one time, ~40GB)
ollama pull llama3.1:70b
ollama pull nomic-embed-text

# 3. Use local embeddings
# No API keys needed!
# Total cost: $0
# Internet: Only for initial download
```

---

## 📊 Performance Comparison (Free APIs)

| Model | Provider | Cost | Speed (tokens/sec) | Quality | Research Friendly |
|-------|----------|------|-------------------|---------|-------------------|
| **Llama-3.1-70B** | Groq | $0 | 750 | ⭐⭐⭐⭐⭐ | ✅ Cite-able, reproducible |
| **Gemini-1.5-Flash** | Google | $0 | 200 | ⭐⭐⭐⭐ | ✅ Good for comparison |
| **Llama-3.1-70B** | Ollama (local) | $0 | 50-100 | ⭐⭐⭐⭐⭐ | ✅ Best for privacy |
| **Mixtral-8x7B** | Groq | $0 | 600 | ⭐⭐⭐⭐ | ✅ Good alternative |

**Winner**: Groq (llama-3.1-70b) - Best balance of speed, quality, and cost ($0!)

---

## 🔬 Research Experiment Costs

### Your 829 Test Intents:

**Baseline Experiment (E1)**:
- Model: Groq llama-3.1-70b
- Requests: 83 (test set)
- Time: ~15 seconds
- Cost: **$0**

**RAG Experiment (E2-E6)** (5 experiments):
- Model: Groq + embeddings
- Requests: 83 × 5 = 415
- Time: ~1.5 minutes
- Cost: **$0**

**Agentic Experiments (E7-E8)** (2 experiments):
- Model: Groq multi-agent
- Requests: 83 × 2 × 4 agents = 664
- Time: ~5 minutes  
- Cost: **$0**

**Total for ALL 8 experiments**: 
- Time: ~7 minutes
- Cost: **$0** 🎉

---

## 🎯 Recommended Free Stack for Your Research

```python
# research_config.py

STACK = {
    # Primary LLM
    "llm": "groq/llama-3.1-70b-versatile",
    "llm_backup": "gemini/gemini-1.5-flash",
    
    # Embeddings (local, no API)
    "embeddings": "sentence-transformers/all-mpnet-base-v2",
    
    # Vector DB (local, no server)
    "vector_db": "chromadb",
    
    # Agentic framework
    "agents": "langgraph",
    
    # Total monthly cost
    "cost": "$0"
}
```

---

## 📝 Research Advantages of Free Stack

### 1. **Reproducibility** ⭐⭐⭐⭐⭐
```markdown
Other researchers can replicate your work:
✅ "We used Groq's free API with llama-3.1-70b"
✅ "Code and full experiment setup: github.com/your-repo"
✅ "Anyone can reproduce for $0"

vs. paid APIs:
❌ "We used GPT-4, results may vary due to model updates"
❌ "Costs $500 to replicate our experiments"
```

### 2. **Scalability**
```markdown
Want to run 100 experiments? Go ahead!
Want to try new ideas? No budget approval needed!
Made a mistake? Re-run everything for $0!
```

### 3. **Academic Credibility**
```markdown
Reviewers love:
✅ Open-source everything
✅ Reproducible on any budget
✅ No corporate dependencies
✅ Transparent methodology
```

### 4. **Groq's Research Speed**
```markdown
Your current performance:
- 829 intents in 2.5 minutes
- That's 5.4 intents/second!
- Iterate FAST on experiments
```

---

## 🚀 Quick Start: RAG with Free Stack

```python
# 1. Setup (one time)
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

# Local embeddings (FREE)
embedder = SentenceTransformer('all-mpnet-base-v2')

# Local vector DB (FREE)
chroma = chromadb.PersistentClient(path="./vector_db")
collection = chroma.create_collection("tmf921")

# Free API
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Index your 663 training examples (one time)
train_data = load_json("data/train_intents.json")
embeddings = embedder.encode([item['user_intent'] for item in train_data])
collection.add(
    embeddings=embeddings.tolist(),
    documents=[item['user_intent'] for item in train_data],
    metadatas=[{"tmf921": json.dumps(item['tmf921_intent'])} 
               for item in train_data],
    ids=[str(i) for i in range(len(train_data))]
)

# 3. RAG Translation Function
def rag_translate(user_intent, k=5):
    # Retrieve similar examples (FREE, local)
    query_embedding = embedder.encode([user_intent])
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=k
    )
    
    # Build prompt with examples
    prompt = f"""Similar TMF921 examples:
{format_examples(results)}

Translate this intent to TMF921:
{user_intent}"""
    
    # Generate with Groq (FREE)
    response = groq.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return parse_tmf921(response.choices[0].message.content)

# 4. Evaluate on test set (FREE!)
test_data = load_json("data/test_intents.json")
results = []
for item in test_data:
    generated = rag_translate(item['user_intent'])
    score = evaluate(generated, item['tmf921_intent'])
    results.append(score)

print(f"Average score: {np.mean(results)}")
print(f"Total cost: $0")
```

---

## 📖 Next Steps

**Week 1: Setup**
```bash
✅ You already have Groq API key
✅ Get Gemini API key (backup)
✅ Install: pip install chromadb sentence-transformers langgraph
✅ Split dataset: train/val/test
✅ Build vector DB from train set
```

**Week 2: Baseline + RAG**
```bash
✅ Run baseline (E1) - should match your current 100% success
✅ Implement RAG retrieval
✅ Run RAG experiments (E2-E6)
✅ Compare results
```

**Week 3: Agentic**
```bash
✅ Design LangGraph workflow
✅ Implement 4 agents
✅ Run agentic experiments (E7-E8)
✅ Final evaluation
```

**Total Timeline**: 3 weeks  
**Total Cost**: **$0** 🎉

---

## ✅ Summary

Your Free Research Stack:
- LLM: Groq (llama-3.1-70b) - $0, 750 tok/sec
- Embeddings: sentence-transformers - $0, local
- Vector DB: ChromaDB - $0, local
- Agents: LangGraph - $0, open-source
- **Total: $0, fully reproducible, faster than paid options!**

**You're actually in a BETTER position than if you were using paid APIs!** 🚀
