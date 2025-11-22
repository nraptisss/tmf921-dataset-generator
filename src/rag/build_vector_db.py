"""
Build ChromaDB vector database from training set
Uses sentence-transformers for embeddings
"""

import json
import os
from pathlib import Path
import argparse
from sentence_transformers import SentenceTransformer
import chromadb
from tqdm import tqdm


def load_training_data(filepath):
    """Load training intent pairs"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def create_embeddings(texts, model_name='all-mpnet-base-v2', batch_size=32):
    """
    Create embeddings for texts using sentence-transformers
    
    Args:
        texts: List of text strings
        model_name: SentenceTransformer model to use
        batch_size: Batch size for encoding
    
    Returns:
        List of embedding vectors
    """
    print(f"\nLoading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    
    print(f"Creating embeddings for {len(texts)} texts...")
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    return embeddings


def build_vector_database(
    train_data,
    db_path='./vector_db',
    collection_name='tmf921_intents',
    embedding_model='all-mpnet-base-v2'
):
    """
    Build ChromaDB vector database from training data
    
    Args:
        train_data: List of intent pairs
        db_path: Path to store ChromaDB
        collection_name: Name of the collection
        embedding_model: SentenceTransformer model name
    
    Returns:
        ChromaDB collection
    """
    # Extract user intents for embedding
    user_intents = [item['user_intent'] for item in train_data]
    
    # Create embeddings
    embeddings = create_embeddings(user_intents, model_name=embedding_model)
    
    # Initialize ChromaDB
    print(f"\nInitializing ChromaDB at: {db_path}")
    client = chromadb.PersistentClient(path=db_path)
    
    # Create or get collection
    try:
        client.delete_collection(name=collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "TMF921 intent pairs for RAG"}
    )
    
    # Add documents to collection
    print(f"\nAdding {len(train_data)} documents to collection...")
    ids = [f"intent_{i}" for i in range(len(train_data))]
    documents = user_intents
    metadatas = [
        {
            "tmf921_intent": json.dumps(item['tmf921_intent']),
            "user_intent": item['user_intent']
        }
        for item in train_data
    ]
    
    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"[OK] Added {len(train_data)} examples to vector database")
    print(f"[OK] Database saved to: {db_path}")
    
    return collection


def test_retrieval(collection, query, k=3):
    """Test retrieval with a sample query"""
    print(f"\n{'=' * 70}")
    print(f"Testing retrieval with query:")
    print(f"  '{query}'")
    print(f"{'=' * 70}\n")
    
    # Create embedding model
    model = SentenceTransformer('all-mpnet-base-v2')
    query_embedding = model.encode([query])[0]
    
    # Query collection
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=k
    )
    
    print(f"Top {k} results:")
    for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
        print(f"{i+1}. (distance: {distance:.4f})")
        print(f"   {doc[:100]}...")
        print()
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Build TMF921 vector database')
    parser.add_argument(
        '--data',
        default='data/train_intents.json',
        help='Training data file'
    )
    parser.add_argument(
        '--db-path',
        default='./vector_db',
        help='Path to store ChromaDB'
    )
    parser.add_argument(
        '--collection',
        default='tmf921_intents',
        help='Collection name'
    )
    parser.add_argument(
        '--model',
        default='all-mpnet-base-v2',
        help='SentenceTransformer model name'
    )
    parser.add_argument(
        '--test-query',
        help='Optional query to test retrieval'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("TMF921 Vector Database Builder")
    print("=" * 70)
    
    # Load training data
    print(f"\nLoading training data from: {args.data}")
    train_data = load_training_data(args.data)
    print(f"Loaded {len(train_data)} training examples")
    
    # Build vector database
    collection = build_vector_database(
        train_data,
        db_path=args.db_path,
        collection_name=args.collection,
        embedding_model=args.model
    )
    
    # Test retrieval
    if args.test_query:
        test_retrieval(collection, args.test_query)
    else:
        # Use a sample query
        sample_query = "Create a network slice for emergency medical services"
        test_retrieval(collection, sample_query)
    
    print("\n" + "=" * 70)
    print("[OK] Vector database ready for RAG experiments!")
    print("=" * 70)
    print(f"\nNext steps:")
    print(f"  1. Run RAG experiments: python experiments/run_experiments.py")
    print(f"  2. Test retrieval: python rag/rag_retriever.py")


if __name__ == "__main__":
    main()

