"""
Intent Categorizer
Analyzes natural language intents and categorizes them for proper TMF921 mapping
"""

import re
from typing import Dict, Tuple


class IntentCategorizer:
    """Categorizes telecom intents and extracts key parameters"""
    
    # Intent category patterns
    CATEGORIES = {
        "ultra_low_latency": {
            "keywords": ["surgery", "autonomous", "emergency", "mission-critical", "v2x", "ultra-low"],
            "latency_range": (1, 10),
            "throughput_range": (50, 200),
            "layer": "resource"
        },
        "low_latency": {
            "keywords": ["gaming", "ar", "vr", "real-time", "live", "low latency", "ping"],
            "latency_range": (10, 30),
            "throughput_range": (100, 300),
            "layer": "resource"
        },
        "high_throughput": {
            "keywords": ["video", "stream", "4k", "hd", "broadcast", "concert", "stadium"],
            "latency_range": (30, 100),
            "throughput_range": (200, 1000),
            "layer": "resource"
        },
        "iot_massive": {
            "keywords": ["iot", "sensor", "massive", "agricultural", "smart meter", "monitoring"],
            "latency_range": (100, 1000),
            "throughput_range": (1, 10),
            "layer": "resource"
},
        "iot_critical": {
            "keywords": ["industrial", "automation", "control", "scada", "manufacturing"],
            "latency_range": (10, 50),
            "throughput_range": (10, 100),
            "layer": "resource"
        },
        "mobile_broadband": {
            "keywords": ["mobile", "broadband", "download", "upload", "connectivity"],
            "latency_range": (20, 100),
            "throughput_range": (100, 500),
            "layer": "resource"
        },
        "edge_computing": {
            "keywords": ["edge", "mec", "cdn", "compute", "processing"],
            "latency_range": (5, 30),
            "throughput_range": (100, 500),
            "layer": "resource"
        },
        "service_delivery": {
            "keywords": ["deploy", "provision", "establish", "setup", "create"],
            "latency_range": (50, 200),
            "throughput_range": (50, 200),
            "layer": "service"
        }
    }
    
    @staticmethod
    def categorize(user_intent: str) -> Dict:
        """
        Categorize a user intent and extract parameters
        
        Args:
            user_intent: Natural language intent description
        
        Returns:
            Dictionary with category, parameters, and metadata
        """
        intent_lower = user_intent.lower()
        
        # Find matching category
        category = "mobile_broadband"  # default
        max_matches = 0
        
        for cat_name, cat_info in IntentCategorizer.CATEGORIES.items():
            matches = sum(1 for keyword in cat_info["keywords"] if keyword in intent_lower)
            if matches > max_matches:
                max_matches = matches
                category = cat_name
        
        cat_info = IntentCategorizer.CATEGORIES[category]
        
        # Extract explicit latency/throughput values if mentioned
        latency = IntentCategorizer._extract_latency(user_intent)
        if latency is None:
            # Use midpoint of category range
            latency = sum(cat_info["latency_range"]) // 2
        
        throughput = IntentCategorizer._extract_throughput(user_intent)
        if throughput is None:
            # Use midpoint of category range
            throughput = sum(cat_info["throughput_range"]) // 2
        
        # Determine service type based on intent
        service_type = IntentCategorizer._determine_service_type(user_intent)
        
        # Generate intent name
        intent_name = IntentCategorizer._generate_intent_name(user_intent)
        
        return {
            "category": category,
            "layer": cat_info["layer"],
            "latency_ms": latency,
            "throughput_mbps": throughput,
            "service_type": service_type,
            "intent_name": intent_name,
            "priority": IntentCategorizer._determine_priority(category),
            "reliability": IntentCategorizer._determine_reliability(category)
        }
    
    @staticmethod
    def _extract_latency(text: str) -> int:
        """Extract latency value from text (in milliseconds)"""
        # Pattern: "below 20ms", "under 10ms", "latency 5ms", etc.
        patterns = [
            r"below\s+(\d+)\s*ms",
            r"under\s+(\d+)\s*ms",
            r"latency\s+(\d+)\s*ms",
            r"ping\s+below\s+(\d+)",
            r"<\s*(\d+)\s*ms"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    @staticmethod
    def _extract_throughput(text: str) -> int:
        """Extract throughput value from text (in MB/s)"""
        # Pattern: "100 MB/s", "5 Gbps", etc.
        patterns = [
            r"(\d+)\s*mb/s",
            r"(\d+)\s*mbps",
            r"(\d+\.?\d*)\s*gbps"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = float(match.group(1))
                if "gbps" in pattern:
                    value *= 125  # Convert Gbps to MB/s
                return int(value)
        
        return None
    
    @staticmethod
    def _determine_service_type(text: str) -> str:
        """Determine the service type from intent text"""
        text_lower = text.lower()
        
        # Service type mapping
        service_types = {
            "NetworkSlice": ["slice", "network", "connectivity"],
            "IoTService": ["iot", "sensor", "device"],
            "EmergencyService": ["emergency", "critical", "rescue"],
            "BroadcastService": ["broadcast", "stream", "video"],
            "EdgeService": ["edge", "mec"],
            "VPNService": ["vpn", "secure", "encrypted"],
            "GamingService": ["gaming", "game", "e-sports"],
            "V2XService": ["v2x", "vehicle", "autonomous driving"],
            "TelehealthService": ["telemedicine", "health", "medical", "hospital"],
            "IndustrialService": ["industrial", "manufacturing", "automation"]
        }
        
        for service_type, keywords in service_types.items():
            if any(keyword in text_lower for keyword in keywords):
                return service_type
        
        return "NetworkSlice"  # default
    
    @staticmethod
    def _generate_intent_name(text: str) -> str:
        """Generate a clean intent name from description"""
        # Take first few significant words
        words = text.split()[:5]
        name = "_".join(w.capitalize() for w in words if len(w) > 3)
        return f"Intent_{name}"
    
    @staticmethod
    def _determine_priority(category: str) -> int:
        """Determine priority based on category (1=highest, 5=lowest)"""
        priority_map = {
            "ultra_low_latency": 1,
            "iot_critical": 1,
            "low_latency": 2,
            "edge_computing": 2,
            "high_throughput": 3,
            "mobile_broadband": 3,
            "iot_massive": 4,
            "service_delivery": 3
        }
        return priority_map.get(category, 3)
    
    @staticmethod
    def _determine_reliability(category: str) -> str:
        """Determine reliability requirement based on category"""
        reliability_map = {
            "ultra_low_latency": "99.999%",
            "iot_critical": "99.99%",
            "low_latency": "99.9%",
            "edge_computing": "99.9%",
            "high_throughput": "99.5%",
            "mobile_broadband": "99.0%",
            "iot_massive": "95.0%",
            "service_delivery": "99.0%"
        }
        return reliability_map.get(category, "99.0%")


if __name__ == "__main__":
    # Test categorizer
    test_intents = [
        "Create a high-speed network slice for a hospital remote surgery robot requiring ultra-low latency.",
        "Deploy a massive IoT network for agricultural sensors with low bandwidth requirements.",
        "Create a gaming slice with guaranteed ping below 20ms for e-sports tournament.",
        "Setup a dedicated connection for emergency response vehicles with highest priority.",
        "Ensure high throughput for a stadium concert video stream.",
    ]
    
    print("Testing Intent Categorizer")
    print("=" * 80)
    
    for intent in test_intents:
        result = IntentCategorizer.categorize(intent)
        print(f"\nIntent: {intent[:70]}...")
        print(f"  Category: {result['category']}")
        print(f"  Service Type: {result['service_type']}")
        print(f"  Latency: {result['latency_ms']} ms")
        print(f"  Throughput: {result['throughput_mbps']} MB/s")
        print(f"  Priority: {result['priority']}")
        print(f"  Intent Name: {result['intent_name']}")
