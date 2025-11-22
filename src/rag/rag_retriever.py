"""
RAG Retriever for TMF921 Intent Translation
Supports multiple retrieval strategies
"""

import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import chromadb


class RAGRetriever:
    """Retrieval-Augmented Generation retriever for TMF921 intents"""
    
    def __init__(
        self,
        db_path: str = './vector_db',
        collection_name: str = 'tmf921_intents',
        embedding_model: str = 'all-mpnet-base-v2'
    ):
        """
        Initialize RAG retriever
        
        Args:
            db_path: Path to ChromaDB
            collection_name: Name of the collection
            embedding_model: SentenceTransformer model name
        """
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Load embedding model
        print(f"Loading embedding model: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        
        # Connect to ChromaDB
        print(f"Connecting to ChromaDB: {db_path}")
        client = chromadb.PersistentClient(path=db_path)
        self.collection = client.get_collection(name=collection_name)
        
        print(f"[OK] RAG Retriever initialized")
        print(f"  Collection size: {self.collection.count()} examples")
    
    def retrieve_top_k(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-K most similar examples
        
        Args:
            query: User intent query
            k: Number of examples to retrieve
        
        Returns:
            List of retrieved examples with metadata
        """
        # Embed the query manually to match database dimensions
        query_embedding = self.embedder.encode([query])[0]
        
        # Query the collection with embedding
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k
        )
        
        # Format results
        examples = []
        for i in range(len(results['documents'][0])):
            example = {
                'user_intent': results['documents'][0][i],
                'tmf921_intent': json.loads(results['metadatas'][0][i]['tmf921_intent']),
                'distance': results['distances'][0][i],
                'id': results['ids'][0][i]
            }
            examples.append(example)
        
        return examples
    
    def retrieve_mmr(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Maximal Marginal Relevance retrieval
        Balances relevance and diversity
        
        Args:
            query: User intent query
            k: Number of examples to return
            fetch_k: Number of candidates to fetch initially
            lambda_mult: Balance between relevance (1.0) and diversity (0.0)
        
        Returns:
            List of retrieved examples
        """
        # Fetch more candidates
        candidates = self.retrieve_top_k(query, k=fetch_k)
        
        if len(candidates) <= k:
            return candidates
        
        # Get query embedding
        query_emb = self.embedder.encode([query])[0]
        
        # Get candidate embeddings
        candidate_texts = [c['user_intent'] for c in candidates]
        candidate_embs = self.embedder.encode(candidate_texts)
        
        # MMR selection
        selected = []
        selected_indices = []
        
        while len(selected) < k:
            best_score = -float('inf')
            best_idx = -1
            
            for i, candidate in enumerate(candidates):
                if i in selected_indices:
                    continue
                
                # Relevance: similarity to query
                relevance = self._cosine_similarity(query_emb, candidate_embs[i])
                
                # Diversity: min similarity to selected
                if selected_indices:
                    similarities = [
                        self._cosine_similarity(candidate_embs[i], candidate_embs[j])
                        for j in selected_indices
                    ]
                    diversity = 1 - max(similarities)
                else:
                    diversity = 1.0
                
                # MMR score
                score = lambda_mult * relevance + (1 - lambda_mult) * diversity
                
                if score > best_score:
                    best_score = score
                    best_idx = i
            
            if best_idx >= 0:
                selected.append(candidates[best_idx])
                selected_indices.append(best_idx)
        
        return selected
    
    def retrieve_hybrid(
        self,
        query: str,
        k: int = 5,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval combining semantic and keyword search
        
        Args:
            query: User intent query
            k: Number of examples to retrieve
            keyword_weight: Weight for keyword matching (0.0-1.0)
        
        Returns:
            List of retrieved examples
        """
        # Semantic search
        semantic_results = self.retrieve_top_k(query, k=k*2)
        
        # Simple keyword scoring
        query_keywords = set(query.lower().split())
        
        for result in semantic_results:
            doc_keywords = set(result['user_intent'].lower().split())
            keyword_overlap = len(query_keywords & doc_keywords) / len(query_keywords)
            
            # Combine scores (invert distance for semantic similarity)
            semantic_score = 1 / (1 + result['distance'])
            combined_score = (
                (1 - keyword_weight) * semantic_score +
                keyword_weight * keyword_overlap
            )
            result['combined_score'] = combined_score
        
        # Re-rank by combined score
        semantic_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return semantic_results[:k]
    
    @staticmethod
    def _cosine_similarity(a, b):
        """Compute cosine similarity between two vectors"""
        import numpy as np
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def format_examples_for_prompt(
        self,
        examples: List[Dict[str, Any]],
        max_examples: int = 3
    ) -> str:
        """
        Format retrieved examples for LLM prompt
        
        Args:
            examples: Retrieved examples
            max_examples: Maximum number to include
        
        Returns:
            Formatted string for prompt
        """
        formatted = []
        
        for i, example in enumerate(examples[:max_examples], 1):
            formatted.append(f"Example {i}:")
            formatted.append(f"User Intent: {example['user_intent']}")
            formatted.append(f"TMF921 Intent:")
            formatted.append(json.dumps(example['tmf921_intent'], indent=2))
            formatted.append("")
        
        return "\n".join(formatted)


# Test the retriever
if __name__ == "__main__":
    # Initialize retriever
    retriever = RAGRetriever()
    
    # Test queries
    test_queries = [
        "Create a hospital emergency network with ultra-low latency",
        "Deploy IoT sensors for agriculture",
        "Setup VPN for financial trading"
    ]
    
    print("\n" + "=" * 70)
    print("TESTING RAG RETRIEVAL STRATEGIES")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\nQuery: {query}\n")
        
        # Top-K
        print("Top-K Retrieval (k=3):")
        topk_results = retriever.retrieve_top_k(query, k=3)
        for i, r in enumerate(topk_results, 1):
            print(f"  {i}. {r['user_intent'][:60]}... (dist: {r['distance']:.4f})")
        
        # MMR
        print("\nMMR Retrieval (k=3):")
        mmr_results = retriever.retrieve_mmr(query, k=3)
        for i, r in enumerate(mmr_results, 1):
            print(f"  {i}. {r['user_intent'][:60]}... (dist: {r['distance']:.4f})")
        
        print("-" * 70)
