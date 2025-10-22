
"""
Utility Functions Module
Provides helper functions for data conversion and JSON serialization.
"""

import json
import logging
from decimal import Decimal
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DecimalEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle Decimal types from DynamoDB.
    
    Converts Decimal objects to appropriate numeric types (int or float)
    during JSON serialization to ensure compatibility with JSON format.
    """
    
    def default(self, obj: Any) -> Any:
        """
        Override default method to handle Decimal conversion.
        
        Args:
            obj: Object to be serialized
            
        Returns:
            Serializable representation of the object
        """
        try:
            if isinstance(obj, Decimal):
                # Convert to int if it's a whole number, otherwise float
                return float(obj) if obj % 1 else int(obj)
            return super(DecimalEncoder, self).default(obj)
        except Exception as e:
            logger.error(f"Error encoding object {obj}: {e}")
            # Fallback to string representation
            return str(obj)