"""
Intent Translator
Translates natural language telecom intents into TMF921-compliant JSON structures
"""

import json
import logging
from typing import Dict, Optional
from llm_interface import LLMInterface
from tmf921_templates import TMF921Templates
from intent_categorizer import IntentCategorizer

logger = logging.getLogger(__name__)


class IntentTranslator:
    """Translates natural language intents to TMF921 format using LLM"""
    
    def __init__(self, llm: LLMInterface):
        """
        Initialize the translator
        
        Args:
            llm: LLMInterface instance
        """
        self.llm = llm
        self.templates = TMF921Templates()
        self.categorizer = IntentCategorizer()
    
    def translate(self, user_intent: str, intent_index: int = 1) -> Dict:
        """
        Translate a user intent to TMF921 format
        
        Args:
            user_intent: Natural language intent description
            intent_index: Index number for the intent
        
        Returns:
            TMF921-compliant Intent JSON structure
        """
        # First, categorize the intent to get parameters
        category_info = self.categorizer.categorize(user_intent)
        
        logger.info(f"Translating intent {intent_index}: {user_intent[:50]}...")
        logger.info(f"  Category: {category_info['category']}, Service: {category_info['service_type']}")
        
        # Build the prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(user_intent, category_info, intent_index)
        
        # Generate TMF921 intent using LLM
        try:
            response = self.llm.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=3000,
                json_mode=True
            )
            
            # Parse the JSON response
            intent_json = json.loads(response)
            
            # Validate basic structure
            if not self._validate_basic_structure(intent_json):
                logger.warning("Generated intent failed basic validation, falling back to template")
                intent_json = self._fallback_to_template(user_intent, category_info, intent_index)
            
            return intent_json
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.info("Falling back to template-based generation")
            return self._fallback_to_template(user_intent, category_info, intent_index)
        
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return self._fallback_to_template(user_intent, category_info, intent_index)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the LLM"""
        return """You are an expert in TMForum TMF921 Intent Management specification and telecom network intent modeling.

Your task is to translate natural language telecom intents into TMF921-compliant Intent JSON structures with Turtle RDF expressions.

CRITICAL REQUIREMENTS:
1. Generate ONLY valid JSON, no additional text or explanations
2. Use proper Turtle RDF syntax with correct escape sequences
3. Include all required namespaces and prefixes
4. Follow TMF921 v5.0.0 specification exactly
5. Ensure all quotes in Turtle expressions are properly escaped
6. Use appropriate intent layers (resource, service, or network)
7. Include PropertyExpectation or DeliveryExpectation as appropriate
8. Always include ReportingExpectation with standard triggers

KEY TMF921 STRUCTURE:
- Intent must have: name, description, expression (with Turtle RDF), lifecycleStatus, timestamps
- Turtle expression must include: intent declaration, targets, expectations, conditions, utility functions,reporting
- Use icm:, imo:, quan:, logi:, set:, and other TMF namespaces correctly

Output ONLY the JSON structure, nothing else."""
    
    def _build_user_prompt(self, user_intent: str, category_info: Dict, index: int) -> str:
        """Build the user prompt with context and examples"""
        
        example_intent = self._get_reference_example(category_info['category'])
        
        prompt = f"""Translate this telecom intent into TMF921-compliant JSON:

USER INTENT: "{user_intent}"

CONTEXT (use these parameters):
- Intent Index: {index}
- Category: {category_info['category']}
- Service Type: {category_info['service_type']}
- Layer: {category_info['layer']}
- Target Latency: {category_info['latency_ms']} ms
- Target Throughput: {category_info['throughput_mbps']} MB/s
- Priority: {category_info['priority']}
- Suggested Intent Name: {category_info['intent_name']}_{index}

REFERENCE EXAMPLE (follow this structure):
{json.dumps(example_intent, indent=2)}

INSTRUCTIONS:
1. Generate a complete TMF921 Intent JSON with Turtle RDF expression
2. Create a unique intent ID based on the user intent: idan:{category_info['intent_name']}_{index}
3. Use PropertyExpectation for performance requirements (latency, throughput)
4. Use DeliveryExpectation for simple service provisioning
5. Include utility functions with logistic curves for latency and throughput
6. Add reporting expectations with event triggers
7. Ensure ALL string values in Turtle are properly quoted and escaped
8. Use current timestamp for creationDate and statusChangeDate

Generate the complete TMF921 Intent JSON now:"""
        
        return prompt
    
    def _get_reference_example(self, category: str) -> Dict:
        """Get a reference example based on category"""
        # For PropertyExpectation-based intents
        if category in ["ultra_low_latency", "low_latency", "high_throughput", "iot_critical", "edge_computing"]:
            turtle = self.templates.create_property_expectation_turtle(
                intent_id="ExampleIntent",
                service_type="ExampleService",
                latency_value=20,
                throughput_value=150
            )
            return self.templates.create_base_intent_json(
                name="ExampleIntent",
                description="Example intent for reference",
                turtle_expression=turtle
            )
        # For DeliveryExpectation-based intents
        else:
            turtle = self.templates.create_delivery_expectation_turtle(
                intent_id="ExampleServiceIntent",
                service_type="ExampleService"
            )
            return self.templates.create_base_intent_json(
                name="ExampleServiceIntent",
                description="Example service delivery intent",
                turtle_expression=turtle
            )
    
    def _validate_basic_structure(self, intent_json: Dict) -> bool:
        """Validate basic TMF921 structure"""
        required_fields = ['name', 'description', 'expression', 'lifecycleStatus', 'creationDate']
        
        # Check top-level fields
        for field in required_fields:
            if field not in intent_json:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Check expression structure
        if 'expression' in intent_json:
            expr = intent_json['expression']
            if '@type' not in expr or expr.get('@type') != 'TurtleExpression':
                logger.warning("Invalid expression type")
                return False
            
            if 'expressionValue' not in expr or not expr['expressionValue']:
                logger.warning("Missing expressionValue")
                return False
        
        return True
    
    def _fallback_to_template(self, user_intent: str, category_info: Dict, index: int) -> Dict:
        """Generate intent using template as fallback"""
        logger.info("Using template-based fallback generation")
        
        intent_name = f"{category_info['intent_name']}_{index}"
        
        # Choose template type based on category
        if category_info['layer'] == 'service':
            turtle = self.templates.create_delivery_expectation_turtle(
                intent_id=intent_name,
                service_type=category_info['service_type'],
                layer=category_info['layer']
            )
        else:
            turtle = self.templates.create_property_expectation_turtle(
                intent_id=intent_name,
                service_type=category_info['service_type'],
                latency_value=category_info['latency_ms'],
                throughput_value=category_info['throughput_mbps'],
                layer=category_info['layer']
            )
        
        return self.templates.create_base_intent_json(
            name=intent_name,
            description=user_intent,
            turtle_expression=turtle
        )


if __name__ == "__main__":
    # Test the translator
    import os
    logging.basicConfig(level=logging.INFO)
    
    # Check if API key is set
    if not os.getenv("GROQ_API_KEY"):
        print("⚠ GROQ_API_KEY not set. Please create a .env file with your API key.")
        print("  Get your free key at: https://console.groq.com/")
        exit(1)
    
    try:
        # Initialize
        llm = LLMInterface(provider="groq")
        translator = IntentTranslator(llm)
        
        # Test intent
        test_intent = "Create a high-speed network slice for a hospital remote surgery robot requiring ultra-low latency."
        
        print(f"\nTranslating: {test_intent}")
        print("=" * 80)
        
        result = translator.translate(test_intent, intent_index=1)
        
        print("\n✓ Translation successful!")
        print(f"Intent Name: {result['name']}")
        print(f"Description: {result['description']}")
        print(f"Lifecycle Status: {result['lifecycleStatus']}")
        print(f"\nTurtle Expression (first 500 chars):")
        print(result['expression']['expressionValue'][:500] + "...")
        
        # Save to file for inspection
        with open("test_intent_output.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n✓ Full output saved to: test_intent_output.json")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
