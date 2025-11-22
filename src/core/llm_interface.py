"""
LLM Interface for TMF921 Dataset Generation
Supports multiple API providers with focus on Groq
"""

import os
import json
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised when API rate limit is hit"""
    pass


class LLMInterface:
    """Multi-provider LLM interface with primary focus on Groq"""
    
    def __init__(self, provider: str = "groq"):
        """
        Initialize LLM interface
        
        Args:
            provider: API provider to use ('groq', 'gemini', 'together')
        """
        self.provider = provider.lower()
        self.client = None
        self.model = None
        self.tokens_used = {"prompt": 0, "completion": 0, "total": 0}
        
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the selected API provider"""
        if self.provider == "groq":
            self._init_groq()
        elif self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "together":
            self._init_together()
        elif self.provider == "huggingface" or self.provider == "hf":
            self._init_huggingface()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _init_groq(self):
        """Initialize Groq API"""
        try:
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            self.client = Groq(api_key=api_key)
            # Use llama-3.3-70b (updated model, 3.1 deprecated)
            self.model = "llama-3.3-70b-versatile"
            logger.info(f"Initialized Groq with model: {self.model}")
        except ImportError:
            raise ImportError("groq package not installed. Run: pip install groq")
    
    def _init_gemini(self):
        """Initialize Google Gemini API"""
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            genai.configure(api_key=api_key)
            # Use gemini-2.5-flash (fast, free model)
            self.model = "gemini-2.5-flash"
            self.client = genai.GenerativeModel(self.model)
            logger.info(f"Initialized Gemini with model: {self.model}")
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
    
    def _init_together(self):
        """Initialize Together AI API"""
        try:
            from together import Together
            api_key = os.getenv("TOGETHER_API_KEY")
            if not api_key:
                raise ValueError("TOGETHER_API_KEY not found in environment variables")
            
            self.client = Together(api_key=api_key)
            self.model = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
            logger.info(f"Initialized Together AI with model: {self.model}")
        except ImportError:
            raise ImportError("together package not installed. Run: pip install together")
    
    def _init_huggingface(self):
        """Initialize HuggingFace Inference API"""
        try:
            from huggingface_hub import InferenceClient
            api_key = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
            if not api_key:
                raise ValueError("HUGGINGFACE_API_KEY or HF_TOKEN not found in environment variables")
            
            self.client = InferenceClient(token=api_key)
            # Use provider routing - :fastest selects fastest available provider
            # Model will be routed to best available provider (SambaNova, Together, etc.)
            self.model = "Qwen/Qwen2.5-72B-Instruct:fastest"
            logger.info(f"Initialized HuggingFace with model: {self.model}")
        except ImportError:
            raise ImportError("huggingface_hub package not installed. Run: pip install huggingface_hub")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(RateLimitError)
    )
    def generate(self, 
                 system_prompt: str, 
                 user_prompt: str, 
                 temperature: float = 0.7,
                 max_tokens: int = 4096,
                 json_mode: bool = True) -> str:
        """
        Generate text using the configured LLM provider
        
        Args:
            system_prompt: System instruction
            user_prompt: User query
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            json_mode: Enable JSON output mode (if supported)
        
        Returns:
            Generated text response
        """
        try:
            if self.provider == "groq":
                return self._generate_groq(system_prompt, user_prompt, temperature, max_tokens, json_mode)
            elif self.provider == "gemini":
                return self._generate_gemini(system_prompt, user_prompt, temperature, max_tokens)
            elif self.provider == "together":
                return self._generate_together(system_prompt, user_prompt, temperature, max_tokens)
            elif self.provider == "huggingface" or self.provider == "hf":
                return self._generate_huggingface(system_prompt, user_prompt, temperature, max_tokens)
        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            raise
    
    def _generate_groq(self, system_prompt: str, user_prompt: str, 
                       temperature: float, max_tokens: int, json_mode: bool) -> str:
        """Generate using Groq API"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Groq supports JSON mode for structured output
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**kwargs)
            
            # Track token usage
            if hasattr(response, 'usage'):
                self.tokens_used["prompt"] += response.usage.prompt_tokens
                self.tokens_used["completion"] += response.usage.completion_tokens
                self.tokens_used["total"] += response.usage.total_tokens
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "limit" in error_msg or "429" in error_msg:
                logger.warning("Rate limit hit, will retry...")
                raise RateLimitError(str(e))
            raise
    
    def _generate_gemini(self, system_prompt: str, user_prompt: str, 
                         temperature: float, max_tokens: int) -> str:
        """Generate using Gemini API"""
        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.client.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            
            return response.text
            
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "quota" in error_msg or "429" in error_msg:
                logger.warning("Rate limit hit, will retry...")
                raise RateLimitError(str(e))
            raise
    
    def _generate_together(self, system_prompt: str, user_prompt: str,
                           temperature: float, max_tokens: int) -> str:
        """Generate using Together AI API"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "limit" in error_msg or "429" in error_msg:
                logger.warning("Rate limit hit, will retry...")
                raise RateLimitError(str(e))
            raise
    
    def _generate_huggingface(self, system_prompt: str, user_prompt: str,
                              temperature: float, max_tokens: int) -> str:
        """Generate using HuggingFace Inference API"""
        try:
            # Format as chat messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Use the chat_completion method (not nested)
            response = self.client.chat_completion(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Extract content from response
            if hasattr(response, 'choices') and response.choices:
                return response.choices[0].message.content
            else:
                raise ValueError(f"Unexpected response format: {response}")
            
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "limit" in error_msg or "429" in error_msg:
                logger.warning("Rate limit hit, will retry...")
                raise RateLimitError(str(e))
            raise
    
    def get_token_stats(self) -> Dict[str, int]:
        """Get token usage statistics"""
        return self.tokens_used.copy()
    
    def reset_token_stats(self):
        """Reset token usage counters"""
        self.tokens_used = {"prompt": 0, "completion": 0, "total": 0}


if __name__ == "__main__":
    # Test the LLM interface
    logging.basicConfig(level=logging.INFO)
    
    try:
        llm = LLMInterface(provider="groq")
        print(f"✓ Initialized {llm.provider} with model: {llm.model}")
        
        # Test generation
        response = llm.generate(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say 'Hello, World!' in JSON format with a 'message' field.",
            temperature=0.7,
            json_mode=True
        )
        
        print(f"✓ Test generation successful:")
        print(response)
        print(f"\nToken usage: {llm.get_token_stats()}")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
