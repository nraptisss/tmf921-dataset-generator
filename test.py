"""
Quick Testing Utility
Test individual components rapidly
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_single_intent(intent_text):
    """Test translating a single intent"""
    from core.llm_interface import LLMInterface
    from core.intent_translator import IntentTranslator
    import json
    
    print(f"\n[TEST] Intent Translation")
    print(f"Intent: {intent_text}")
    print("-" * 70)
    
    llm = LLMInterface(provider="groq")
    translator = IntentTranslator(llm=llm)
    
    result = translator.translate(intent_text)
    
    print("\n[OK] Result:")
    print(json.dumps(result, indent=2))
    
    return result

def test_rag_translation(intent_text, k=5):
    """Test RAG translation"""
    from rag.rag_translator import RAGTranslator
    import json
    
    print(f"\n[TEST] RAG Translation (k={k})")
    print(f"Intent: {intent_text}")
    print("-" * 70)
    
    translator = RAGTranslator(llm_provider="groq", k=k)
    
    result = translator.translate(intent_text)
    
    print("\n[OK] Result:")
    print(json.dumps(result, indent=2))
    
    return result

def test_retrieval(query, k=5):
    """Test RAG retrieval only"""
    from rag.rag_retriever import RAGRetriever
    
    print(f"\n[TEST] RAG Retrieval (k={k})")
    print(f"Query: {query}")
    print("-" * 70)
    
    retriever = RAGRetriever(db_path="./vector_db")
    
    results = retriever.retrieve_top_k(query, k=k)
    
    print(f"\n[RESULTS] Top {k} Retrieved Examples:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Distance: {result['distance']:.4f}")
        print(f"   Intent: {result['user_intent'][:100]}...")
    
    return results

def test_database():
    """Test vector database connectivity"""
    import chromadb
    
    print("\n[TEST] Vector Database")
    print("-" * 70)
    
    try:
        client = chromadb.PersistentClient(path="./vector_db")
        collection = client.get_collection("tmf921_intents")
        count = collection.count()
        
        print(f"[OK] Database OK")
        print(f"   Collection: tmf921_intents")
        print(f"   Documents: {count}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Database Error: {e}")
        return False

def test_llm():
    """Test LLM connectivity"""
    from core.llm_interface import LLMInterface
    
    print("\n[TEST] LLM Connection")
    print("-" * 70)
    
    try:
        llm = LLMInterface(provider="groq")
        response = llm.generate(
            "You are helpful",
            "Say 'Hello' in JSON with greeting field",
            json_mode=True
        )
        
        print(f"[OK] LLM OK (Groq)")
        print(f"   Response: {response[:100]}...")
        
        return True
    except Exception as e:
        print(f"[ERROR] LLM Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Quick Testing')
    parser.add_argument('intent', nargs='?', help='Intent to test')
    parser.add_argument('--rag', action='store_true', help='Test with RAG')
    parser.add_argument('--retrieval', help='Test retrieval only')
    parser.add_argument('--database', action='store_true', help='Test database')
    parser.add_argument('--llm', action='store_true', help='Test LLM')
    parser.add_argument('-k', type=int, default=5, help='Number of examples (default: 5)')
    
    args = parser.parse_args()
    
    if args.database:
        test_database()
    elif args.llm:
        test_llm()
    elif args.retrieval:
        test_retrieval(args.retrieval, k=args.k)
    elif args.intent:
        if args.rag:
            test_rag_translation(args.intent, k=args.k)
        else:
            test_single_intent(args.intent)
    else:
        # Run all tests
        print("[TEST] Running All Tests\n")
        test_llm()
        test_database()
        print("\n" + "=" * 70)
        print("[OK] All tests complete!")

if __name__ == "__main__":
    main()
