"""
TMF921 Intent Templates
Provides template structures for TMF921-compliant intents
"""

from datetime import datetime, timezone
import uuid


class TMF921Templates:
    """Template generator for TMF921 Intent structures"""
    
    # Common namespace prefixes for Turtle RDF
    TURTLE_PREFIXES = """@prefix icm:  <http://tio.models.tmforum.org/tio/v3.2.0/IntentCommonModel#> .
@prefix imo:  <http://tio.models.tmforum.org/tio/v3.2.0/IntentManagmentOntology#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix idan: <http://www.example.org/IDAN3#> .
@prefix t:    <http://www.w3.org/2006/time#> .
@prefix logi:  <http://tio.models.tmforum.org/tio/v3.2.0/LogicalOperators#> .
@prefix quan: <http://tio.models.tmforum.org/tio/v3.2.0/QuantityOntology#> .
@prefix set:  <http://tio.models.tmforum.org/tio/v3.2.0/SetOperators#> .
@prefix fun:  <http://tio.models.tmforum.org/tio/v3.2.0/FunctionOntology#> .
@prefix ui: <http://www..example.org/ui#> .
@prefix mf: <http://www..example.org/mf#> .
@prefix cem: <http://tio.labs.tmforum.org/tio/v1.0.0/CatalystExtensionModel#> .
@prefix iv: <http://tio.models.tmforum.org/tio/v3.2.0/IntentValidity#> ."""
    
    @staticmethod
    def generate_intent_id(name: str) -> str:
        """Generate a unique intent ID"""
        return f"idan:{name.replace(' ', '_')}"
    
    @staticmethod
    def generate_timestamps():
        """Generate creation and status change timestamps"""
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.000+00:00")
        return {
            "creationDate": timestamp,
            "statusChangeDate": timestamp,
            "lastUpdate": timestamp
        }
    
    @staticmethod
    def create_base_intent_json(
        name: str,
        description: str,
        turtle_expression: str,
        version: str = "1"
    ) -> dict:
        """
        Create base TMF921 Intent JSON structure
        
        Args:
            name: Intent name
            description: Intent description
            turtle_expression: Turtle RDF expression value
            version: Intent version
        
        Returns:
            TMF921-compliant Intent JSON structure
        """
        timestamps = TMF921Templates.generate_timestamps()
        
        return {
            "statusChangeDate": timestamps["statusChangeDate"],
            "expression": {
                "iri": "http://tio.models.tmforum.org/tio/v3.2.0/IntentCommonModel/",
                "@baseType": "Expression",
                "@type": "TurtleExpression",
                "expressionLanguage": "Turtle",
                "expressionValue": turtle_expression,
                "@schemaLocation": "https://mycsp.com:8080/tmf-api/schema/Common/TurtleExpression.schema.json"
            },
            "lifecycleStatus": "Created",
            "@baseType": "Intent",
            "validFor": {
                "startDateTime": "2025-01-01T00:00:00.00Z",
                "endDateTime": "2026-01-01T00:00:00.00Z"
            },
            "@type": "Intent",
            "lastUpdate": timestamps["lastUpdate"],
            "name": name,
            "description": description,
            "creationDate": timestamps["creationDate"],
            "@schemaLocation": "https://mycsp.com:8080/tmf-api/schema/Common/TurtleExpression.schema.json",
            "version": version
        }
    
    @staticmethod
    def create_property_expectation_turtle(
        intent_id: str,
        service_type: str,
        latency_value: int = 50,
        latency_unit: str = "ms",
        throughput_value: int = 100,
        throughput_unit: str = "MB/s",
        layer: str = "resource"
    ) -> str:
        """
        Create Turtle RDF for a PropertyExpectation intent
        
        Args:
            intent_id: Intent identifier (e.g., "Intent_NetworkSlice_1")
            service_type: Type of service (e.g., "NetworkSlice", "IoTService")
            latency_value: Maximum latency value
            latency_unit: Latency unit (ms, us, etc.)
            throughput_value: Minimum throughput value
            throughput_unit: Throughput unit (MB/s, Gbps, etc.)
            layer: Intent layer (resource, service, network)
        
        Returns:
            Turtle RDF expression string
        """
        target_id = f"{intent_id}_Target"
        expectation_id = f"{intent_id}_Expectation"
        condition_id = f"{intent_id}_Condition"
        utility_latency_id = f"{intent_id}_Utility_Latency"
        utility_throughput_id = f"{intent_id}_Utility_Throughput"
        event_id = f"{intent_id}_Event"
        reporting_id = f"{intent_id}_Reporting"
        
        turtle = f"""{TMF921Templates.TURTLE_PREFIXES}

# Intent
idan:{intent_id}
  a icm:Intent ;
  cem:layer idan:{layer} ;
  imo:intentOwner idan:NetworkOperator ;
  icm:hasExpectation idan:{expectation_id},
                     idan:{reporting_id}
.

# Target
idan:{target_id}
  a icm:Target ;
  icm:chooseFrom [ set:resourcesOfType idan:{service_type} ]
.

# Property Expectation
idan:{expectation_id}
  a icm:PropertyExpectation ;
  icm:target idan:{target_id} ;
  logi:allOf [rdfs:member idan:{condition_id} ]
.

# Utility function for latency
idan:{utility_latency_id}
  a mf:LogisticFunction ;
  a ui:Utility ;
  mf:functionInput idan:Latency ;
  mf:midpoint {latency_value // 2} ;
  mf:supremum 1.0 ;
  mf:logisticGrowth -0.2 ;
  iv:validIf [ a icm:Condition;
               quan:atLeast [ idan:Latency [ rdf:value 0 ] ];
               quan:atMost [ idan:Latency [ rdf:value {latency_value * 2} ] ]
             ]
.

# Utility function for throughput
idan:{utility_throughput_id}
  a mf:LogisticFunction ;
  a ui:Utility ;
  mf:functionInput idan:Throughput ;
  mf:midpoint {throughput_value} ;
  mf:supremum 1.0 ;
  mf:logisticGrowth 0.05 ;
  iv:validIf [ a icm:Condition;
               quan:atLeast [ idan:Throughput [ rdf:value {throughput_value // 2} ] ];
               quan:atMost [ idan:Throughput [ rdf:value {throughput_value * 2} ] ]
             ]
.

# Conditions
idan:{condition_id}
  a icm:Condition ;
  rdfs:label "" ;
  quan:smaller [ idan:Latency
                 [ rdf:value "{latency_value}"^^xsd:decimal ;
                   icm:unit80000 "'{latency_unit}'" ]
               ] ;
  ui:utility idan:{utility_latency_id} ;
  quan:greater [ idan:Throughput
                 [ rdf:value "{throughput_value}"^^xsd:decimal ;
                   icm:unit80000 "'{throughput_unit}'"]
               ];
  ui:utility idan:{utility_throughput_id}
.

# Reporting Event (triggered every 5 minutes)
idan:{event_id}
  a rdfs:Class ;
  rdfs:subClassOf imo:Event ;
  logi:if [ t:after [imo:timeOfLastEvent [rdfs:member idan:{event_id} ;
                                          rdfs:member idan:{intent_id} ]]  ,
                    [t:hasDuration "'PT5M'"^^xsd:duration ] ;
            t:before [ t:hasBeginning imo:Now ] ;
         ] ;
  imo:eventFor idan:{intent_id}
.

# Reporting Expectation
idan:{reporting_id}
  a icm:ReportingExpectation ;
  icm:target idan:{intent_id} ;
  icm:reportDestination [ rdfs:member idan:IntentManager ] ;
  icm:reportTriggers [ rdfs:member imo:IntentRejected ;
                       rdfs:member imo:IntentAccepted ;
                       rdfs:member imo:IntentDegrades ;
                       rdfs:member imo:IntentComplies ;
                       rdfs:member imo:IntentRemoval ;
                       rdfs:member idan:{event_id} ]
."""
        return turtle
    
    @staticmethod
    def create_delivery_expectation_turtle(
        intent_id: str,
        service_type: str,
        layer: str = "service"
    ) -> str:
        """
        Create Turtle RDF for a DeliveryExpectation intent (simpler structure)
        
        Args:
            intent_id: Intent identifier
            service_type: Type of service to deliver
            layer: Intent layer
        
        Returns:
            Turtle RDF expression string
        """
        target_id = f"{intent_id}_Target"
        expectation_id = f"{intent_id}_Expectation"
        event_id = f"{intent_id}_Event"
        reporting_id = f"{intent_id}_Reporting"
        
        turtle = f"""{TMF921Templates.TURTLE_PREFIXES}

# Intent
idan:{intent_id}
  a icm:Intent ;
  cem:layer idan:{layer} ;
  imo:intentOwner idan:ServiceOperator ;
  rdfs:comment "Intent for {service_type}" ;
  icm:hasExpectation idan:{expectation_id},
                        idan:{reporting_id}
.

# Delivery Expectation
idan:{expectation_id}
  a icm:DeliveryExpectation ;
    icm:target idan:{target_id} ;
.

# Target
idan:{target_id}
  a icm:Target ;
  icm:allOf [ rdfs:member idan:{service_type}]
.

# Reporting Event
idan:{event_id}
  a rdfs:Class ;
  rdfs:subClassOf imo:Event ;
  logi:if [ t:after [imo:timeOfLastEvent [rdfs:member idan:{event_id} ;
                                              rdfs:member idan:{intent_id} ]]  ,
                         [t:hasDuration "'PT5M'"^^xsd:duration ] ;
                t:before [ t:hasBeginning imo:Now ] ;
         ] ;
  imo:eventFor idan:{intent_id}
.

# Reporting Expectation
idan:{reporting_id}
  a icm:ReportingExpectation ;
  icm:target idan:{intent_id} ;
  icm:reportDestination [ rdfs:member idan:Operations ] ;
  icm:reportTriggers [ rdfs:member imo:IntentRejected ;
                       rdfs:member imo:IntentAccepted ;
                       rdfs:member imo:IntentDegrades ;
                       rdfs:member imo:IntentComplies ;
                       rdfs:member imo:IntentRemoval ;
                       rdfs:member idan:{event_id} ]
."""
        return turtle


if __name__ == "__main__":
    # Test template generation
    print("Testing TMF921 Template Generation")
    print("=" * 60)
    
    # Test PropertyExpectation template
    intent_id = "Intent_UltraLowLatency_1"
    turtle = TMF921Templates.create_property_expectation_turtle(
        intent_id=intent_id,
        service_type="EmergencyService",
        latency_value=10,
        throughput_value=200
    )
    
    intent_json = TMF921Templates.create_base_intent_json(
        name=intent_id,
        description="Ultra-low latency network slice for emergency services",
        turtle_expression=turtle
    )
    
    print("✓ Generated PropertyExpectation intent")
    print(f"  Name: {intent_json['name']}")
    print(f"  Description: {intent_json['description']}")
    print(f"  Turtle length: {len(turtle)} characters")
    
    # Test DeliveryExpectation template
    intent_id_2 = "Intent_IoTService_1"
    turtle_2 = TMF921Templates.create_delivery_expectation_turtle(
        intent_id=intent_id_2,
        service_type="IoTSensorNetwork"
    )
    
    intent_json_2 = TMF921Templates.create_base_intent_json(
        name=intent_id_2,
        description="IoT sensor network service delivery",
        turtle_expression=turtle_2
    )
    
    print("\n✓ Generated DeliveryExpectation intent")
    print(f"  Name: {intent_json_2['name']}")
    print(f"  Description: {intent_json_2['description']}")
    print(f"  Turtle length: {len(turtle_2)} characters")
