"""
RAG-Enhanced TMF921 Intent Translator
Uses retrieval to improve translation quality
"""

import json
import logging
from typing import Dict, List, Optional
from .rag_retriever import RAGRetriever

# Import from core package
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.llm_interface import LLMInterface
from core.intent_categorizer import IntentCategorizer


class RAGTranslator:
    """TMF921 Intent Translator with RAG enhancement"""
    
    def __init__(
        self,
        llm_provider: str = "groq",
        retrieval_strategy: str = "topk",
        k: int = 5,
        db_path: str = './vector_db',
        collection_name: str = 'tmf921_intents'
    ):
        """
        Initialize RAG Translator
        
        Args:
            llm_provider: LLM provider (groq, gemini, together)
            retrieval_strategy: Retrieval strategy (topk, mmr, hybrid)
            k: Number of examples to retrieve
            db_path: Path to vector database
            collection_name: ChromaDB collection name
        """
        self.llm_provider = llm_provider
        self.retrieval_strategy = retrieval_strategy
        self.k = k
        
        # Initialize components
        print(f"Initializing RAG Translator...")
        print(f"  LLM: {llm_provider}")
        print(f"  Retrieval: {retrieval_strategy} (k={k})")
        
        self.llm = LLMInterface(provider=llm_provider)
        self.retriever = RAGRetriever(
            db_path=db_path,
            collection_name=collection_name
        )
        self.categorizer = IntentCategorizer()
        
        print(f"[OK] RAG Translator initialized\n")
    
    def retrieve_examples(self, user_intent: str):
        """Retrieve similar examples based on strategy"""
        if self.retrieval_strategy == "topk":
            return self.retriever.retrieve_top_k(user_intent, k=self.k)
        elif self.retrieval_strategy == "mmr":
            return self.retriever.retrieve_mmr(user_intent, k=self.k)
        elif self.retrieval_strategy == "hybrid":
            return self.retriever.retrieve_hybrid(user_intent, k=self.k)
        else:
            raise ValueError(f"Unknown retrieval strategy: {self.retrieval_strategy}")
    
    def build_rag_prompt(self, user_intent: str, examples: list) -> str:
        """Build prompt with RAG context"""
        # Categorize user intent
        analysis = self.categorizer.categorize(user_intent)
        
        # Format examples
        examples_text = []
        for i, ex in enumerate(examples[:3], 1):  # Use top 3 for prompt
            examples_text.append(f"\n--- Example {i} ---")
            examples_text.append(f"User Intent: {ex['user_intent']}")
            examples_text.append(f"\nTMF921 Intent (JSON with Turtle RDF):")
            examples_text.append(json.dumps(ex['tmf921_intent'], indent=2))
        
        examples_str = "\n".join(examples_text)
        
        system_prompt = """You are an expert TMF921 Intent translator. Your task is to convert natural language telecom intents into TMF921-compliant JSON structures with embedded Turtle RDF expressions.

CRITICAL REQUIREMENTS:
1. Output ONLY valid JSON - no markdown, no code blocks
2. Include all required TMF921 fields
3. Use proper Turtle RDF syntax in expressionValue
4. Include required TMF ontology namespaces (icm, imo, rdf, rdfs, xsd, idan, logi, quan)
5. Follow the patterns shown in the examples below"""

        user_prompt = f"""Using the examples below as reference, translate this telecom intent to TMF921 format:

SIMILAR EXAMPLES FROM TRAINING DATA:
{examples_str}

INTENT TO TRANSLATE:
{user_intent}

INTENT ANALYSIS:
- Service Type: {analysis.get('service_type', 'Unknown')}
- Latency: {analysis.get('latency', 'Unknown')} ms
- Throughput: {analysis.get('throughput', 'Unknown')} MB/s
- Priority: {analysis.get('priority', 'Unknown')}

Generate a complete, valid TMF921 Intent JSON following the pattern above. Output ONLY the JSON, no other text."""

        return system_prompt, user_prompt
    
    def translate(self, user_intent: str) -> dict:
        """
        Translate user intent to TMF921 using RAG
        
        Args:
            user_intent: Natural language telecom intent
        
        Returns:
            TMF921 Intent JSON
        """
        # Retrieve similar examples
        examples = self.retrieve_examples(user_intent)
        
        # Build RAG-enhanced prompt
        system_prompt, user_prompt = self.build_rag_prompt(user_intent, examples)
        
        # Generate with LLM
        response = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,  # Lower temperature for more consistent output
            json_mode=True
        )
        
        # Parse JSON response
        try:
            # Clean response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            tmf921_intent = json.loads(response)
            return tmf921_intent
        
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON response: {e}")
            print(f"Response: {response[:500]}...")
            raise
