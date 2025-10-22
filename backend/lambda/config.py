"""
Configuration Module
Loads application configuration from YAML file.
"""

import yaml
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def load_config():
    """
    Load configuration from YAML file.
    
    Returns:
        dict: Configuration dictionary
        
    Raises:
        Exception: If configuration file cannot be loaded
    """
    try:
        config_file = "config.yaml"
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config_data = yaml.load(f, Loader=yaml.FullLoader)
        
        logger.info(f"Successfully loaded configuration from {config_file}")
        return config_data
        
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        raise Exception(f"Invalid YAML configuration: {e}")
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise Exception(f"Failed to load configuration: {e}")

# Load configuration on module import
config = load_config()