"""
TMF921 Dataset Validator
Validates the generated dataset against TMF921 Intent Management specification
"""

import json
import logging
from typing import Dict, List, Tuple
from pathlib import Path
from collections import defaultdict
import re

# Try to import rdflib for Turtle validation
try:
    from rdflib import Graph
    from rdflib.exceptions import ParserError
    HAS_RDFLIB = True
except ImportError:
    HAS_RDFLIB = False
    print("Warning: rdflib not installed. Turtle RDF validation will be skipped.")
    print("Install with: pip install rdflib")


class TMF921Validator:
    """Validates TMF921 Intent dataset"""
    
    # Required top-level fields for TMF921 Intent
    REQUIRED_INTENT_FIELDS = [
        'name',
        'description',
        'expression',
        'lifecycleStatus',
        'creationDate',
        '@type',
        '@baseType'
    ]
    
    # Required expression fields
    REQUIRED_EXPRESSION_FIELDS = [
        'expressionLanguage',
        'expressionValue',
        '@type',
        'iri'
    ]
    
    # Expected TMF namespaces in Turtle expressions
    EXPECTED_NAMESPACES = [
        '@prefix icm:',
        '@prefix imo:',
        '@prefix rdf:',
        '@prefix rdfs:',
        '@prefix xsd:',
        '@prefix idan:',
        '@prefix logi:',
        '@prefix quan:'
    ]
    
    def __init__(self, dataset_path: str = "output/tmf921_dataset.json"):
        """
        Initialize validator
        
        Args:
            dataset_path: Path to the dataset JSON file
        """
        self.dataset_path = Path(dataset_path)
        self.logger = logging.getLogger(__name__)
        self.validation_results = {
            'total_intents': 0,
            'valid_structure': 0,
            'invalid_structure': 0,
            'valid_turtle': 0,
            'invalid_turtle': 0,
            'valid_tmf921': 0,
            'invalid_tmf921': 0,
            'errors': [],
            'warnings': []
        }
    
    def load_dataset(self) -> Dict:
        """Load the dataset from JSON file"""
        self.logger.info(f"Loading dataset from: {self.dataset_path}")
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        self.validation_results['total_intents'] = len(dataset.get('intent_pairs', []))
        self.logger.info(f"Loaded {self.validation_results['total_intents']} intents")
        
        return dataset
    
    def validate_json_structure(self, intent: Dict, intent_id: int) -> Tuple[bool, List[str]]:
        """
        Validate basic JSON structure of a TMF921 intent
        
        Args:
            intent: TMF921 intent JSON
            intent_id: Intent ID for error reporting
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required top-level fields
        for field in self.REQUIRED_INTENT_FIELDS:
            if field not in intent:
                errors.append(f"Missing required field: {field}")
        
        # Validate expression object
        if 'expression' in intent:
            expr = intent['expression']
            
            # Check expression type
            if expr.get('@type') != 'TurtleExpression':
                errors.append(f"Invalid expression @type: {expr.get('@type')}")
            
            # Check expression language
            if expr.get('expressionLanguage') != 'Turtle':
                errors.append(f"Invalid expressionLanguage: {expr.get('expressionLanguage')}")
            
            # Check required expression fields
            for field in self.REQUIRED_EXPRESSION_FIELDS:
                if field not in expr:
                    errors.append(f"Missing required expression field: {field}")
            
            # Check expressionValue is non-empty
            if not expr.get('expressionValue', '').strip():
                errors.append("Empty expressionValue")
        else:
            errors.append("Missing expression object")
        
        # Validate intent type
        if intent.get('@type') != 'Intent':
            errors.append(f"Invalid @type: {intent.get('@type')}")
        
        if intent.get('@baseType') != 'Intent':
            errors.append(f"Invalid @baseType: {intent.get('@baseType')}")
        
        # Validate lifecycle status
        valid_statuses = ['Created', 'InProgress', 'Active', 'Suspended', 'Terminated']
        if intent.get('lifecycleStatus') not in valid_statuses:
            errors.append(f"Invalid lifecycleStatus: {intent.get('lifecycleStatus')}")
        
        return len(errors) == 0, errors
    
    def validate_turtle_syntax(self, turtle_expression: str, intent_id: int) -> Tuple[bool, List[str]]:
        """
        Validate Turtle RDF syntax
        
        Args:
            turtle_expression: Turtle RDF string
            intent_id: Intent ID for error reporting
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        warnings = []
        
        if not HAS_RDFLIB:
            warnings.append("rdflib not available, skipping Turtle validation")
            return True, warnings  # Don't fail if library not available
        
        try:
            # Try to parse the Turtle RDF
            g = Graph()
            g.parse(data=turtle_expression, format='turtle')
            
            # Check that we parsed some triples
            triple_count = len(g)
            if triple_count == 0:
                errors.append("Turtle expression parsed but contains no triples")
            else:
                self.logger.debug(f"Intent {intent_id}: Parsed {triple_count} RDF triples")
            
        except ParserError as e:
            errors.append(f"Turtle syntax error: {str(e)}")
        except Exception as e:
            errors.append(f"Turtle parsing error: {str(e)}")
        
        return len(errors) == 0, errors + warnings
    
    def validate_tmf921_semantics(self, intent: Dict, intent_id: int) -> Tuple[bool, List[str]]:
        """
        Validate TMF921-specific semantic requirements
        
        Args:
            intent: TMF921 intent JSON
            intent_id: Intent ID for error reporting
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        warnings = []
        
        turtle_expr = intent.get('expression', {}).get('expressionValue', '')
        
        # Check for required namespaces
        missing_namespaces = []
        for ns in self.EXPECTED_NAMESPACES:
            if ns not in turtle_expr:
                missing_namespaces.append(ns.replace('@prefix ', '').replace(':', ''))
        
        if missing_namespaces:
            warnings.append(f"Missing expected namespaces: {', '.join(missing_namespaces)}")
        
        # Check for intent declaration
        intent_name = intent.get('name', '')
        if intent_name and f"idan:{intent_name}" not in turtle_expr:
            warnings.append(f"Intent name '{intent_name}' not found in Turtle expression")
        
        # Check for expectation patterns
        has_expectation = (
            'icm:PropertyExpectation' in turtle_expr or
            'icm:DeliveryExpectation' in turtle_expr or
            'icm:hasExpectation' in turtle_expr
        )
        
        if not has_expectation:
            errors.append("No expectation pattern found in Turtle expression")
        
        # Check for reporting expectation
        if 'icm:ReportingExpectation' not in turtle_expr:
            warnings.append("No ReportingExpectation found")
        
        # Check for target
        if 'icm:Target' not in turtle_expr and 'icm:target' not in turtle_expr:
            warnings.append("No Target found in expression")
        
        # Validate intent layer if present
        if 'cem:layer' in turtle_expr:
            layers = re.findall(r'cem:layer\s+idan:(\w+)', turtle_expr)
            valid_layers = ['resource', 'service', 'network', 'business']
            for layer in layers:
                if layer not in valid_layers:
                    warnings.append(f"Invalid layer: {layer}")
        
        return len(errors) == 0, errors + warnings
    
    def validate_intent(self, intent_pair: Dict) -> Dict:
        """
        Validate a single intent pair
        
        Args:
            intent_pair: Intent pair with user_intent and tmf921_intent
        
        Returns:
            Validation result dictionary
        """
        intent_id = intent_pair.get('id', 'unknown')
        tmf921_intent = intent_pair.get('tmf921_intent', {})
        
        result = {
            'id': intent_id,
            'user_intent': intent_pair.get('user_intent', ''),
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 1. Validate JSON structure
        is_valid_structure, structure_errors = self.validate_json_structure(tmf921_intent, intent_id)
        if not is_valid_structure:
            result['valid'] = False
            result['errors'].extend([f"Structure: {e}" for e in structure_errors])
            self.validation_results['invalid_structure'] += 1
        else:
            self.validation_results['valid_structure'] += 1
        
        # 2. Validate Turtle syntax
        turtle_expr = tmf921_intent.get('expression', {}).get('expressionValue', '')
        if turtle_expr:
            is_valid_turtle, turtle_errors = self.validate_turtle_syntax(turtle_expr, intent_id)
            if not is_valid_turtle:
                result['valid'] = False
                result['errors'].extend([f"Turtle: {e}" for e in turtle_errors if 'Warning' not in str(e)])
                result['warnings'].extend([e for e in turtle_errors if 'Warning' in str(e)])
                self.validation_results['invalid_turtle'] += 1
            else:
                self.validation_results['valid_turtle'] += 1
                result['warnings'].extend(turtle_errors)  # May contain warnings even if valid
        
        # 3. Validate TMF921 semantics
        is_valid_tmf921, tmf921_errors = self.validate_tmf921_semantics(tmf921_intent, intent_id)
        if not is_valid_tmf921:
            result['valid'] = False
            result['errors'].extend([f"TMF921: {e}" for e in tmf921_errors if 'Warning' not in str(e)])
            result['warnings'].extend([e for e in tmf921_errors if 'Warning' in str(e)])
            self.validation_results['invalid_tmf921'] += 1
        else:
            self.validation_results['valid_tmf921'] += 1
            result['warnings'].extend(tmf921_errors)  # May contain warnings even if valid
        
        return result
    
    def validate_dataset(self) -> Dict:
        """
        Validate entire dataset
        
        Returns:
            Validation results summary
        """
        dataset = self.load_dataset()
        intent_pairs = dataset.get('intent_pairs', [])
        
        self.logger.info("Starting validation...")
        
        validation_details = []
        error_count = 0
        warning_count = 0
        
        for intent_pair in intent_pairs:
            result = self.validate_intent(intent_pair)
            
            if not result['valid']:
                error_count += 1
                self.validation_results['errors'].append(result)
                
                # Log first 5 errors in detail
                if error_count <= 5:
                    self.logger.error(f"Intent {result['id']}: FAILED")
                    for error in result['errors']:
                        self.logger.error(f"  - {error}")
            
            if result['warnings']:
                warning_count += len(result['warnings'])
                
                # Log first 3 warnings
                if warning_count <= 10:
                    for warning in result['warnings'][:3]:
                        self.logger.warning(f"Intent {result['id']}: {warning}")
            
            validation_details.append(result)
        
        # Calculate overall statistics
        total = self.validation_results['total_intents']
        valid = sum(1 for r in validation_details if r['valid'])
        
        self.validation_results['overall_valid'] = valid
        self.validation_results['overall_invalid'] = total - valid
        self.validation_results['success_rate'] = (valid / total * 100) if total > 0 else 0
        
        # Save detailed results
        self._save_validation_report(validation_details)
        
        return self.validation_results
    
    def _save_validation_report(self, validation_details: List[Dict]):
        """Save detailed validation report"""
        report_path = self.dataset_path.parent / "validation_report.json"
        
        report = {
            'summary': self.validation_results,
            'details': validation_details
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Validation report saved to: {report_path}")
    
    def print_summary(self):
        """Print validation summary"""
        results = self.validation_results
        
        print("\n" + "=" * 80)
        print("TMF921 DATASET VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total Intents:        {results['total_intents']}")
        print(f"Overall Valid:        {results.get('overall_valid', 0)} ({results.get('success_rate', 0):.1f}%)")
        print(f"Overall Invalid:      {results.get('overall_invalid', 0)}")
        print()
        print("Structure Validation:")
        print(f"  Valid:              {results['valid_structure']}")
        print(f"  Invalid:            {results['invalid_structure']}")
        print()
        
        if HAS_RDFLIB:
            print("Turtle RDF Validation:")
            print(f"  Valid:              {results['valid_turtle']}")
            print(f"  Invalid:            {results['invalid_turtle']}")
            print()
        else:
            print("Turtle RDF Validation: SKIPPED (rdflib not installed)")
            print()
        
        print("TMF921 Semantics Validation:")
        print(f"  Valid:              {results['valid_tmf921']}")
        print(f"  Invalid:            {results['invalid_tmf921']}")
        print()
        
        if results.get('errors'):
            print(f"Failed Intents:       {len(results['errors'])}")
            print("\nFirst 5 errors:")
            for error in results['errors'][:5]:
                print(f"  Intent {error['id']}: {error.get('user_intent', '')[:60]}...")
                for err_msg in error['errors'][:2]:
                    print(f"    - {err_msg}")
        
        print("=" * 80)


def main():
    """Main validation function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\nTMF921 Dataset Validator")
    print("=" * 80)
    
    validator = TMF921Validator("output/tmf921_dataset.json")
    results = validator.validate_dataset()
    validator.print_summary()
    
    print(f"\n✓ Validation complete!")
    print(f"  Detailed report: output/validation_report.json")
    
    # Return exit code based on validation success
    if results.get('overall_invalid', 0) > 0:
        print(f"\n⚠ {results['overall_invalid']} intents failed validation")
        return 1
    else:
        print(f"\n✓ All {results['total_intents']} intents passed validation!")
        return 0


if __name__ == "__main__":
    exit(main())
