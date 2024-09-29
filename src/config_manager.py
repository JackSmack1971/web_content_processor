import yaml
import json
from typing import Any, Dict

class ConfigManager:
    """Manages configuration settings for the integrated application."""

    def __init__(self, config_file: str):
        """
        Initialize the ConfigManager.

        Args:
            config_file (str): Path to the main configuration file.
        """
        self.config: Dict[str, Any] = {}
        self.load_config(config_file)

    def load_config(self, config_file: str) -> None:
        """
        Load configuration from a file.

        Args:
            config_file (str): Path to the configuration file.
        """
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.yaml'):
                    self.config = yaml.safe_load(f)
                elif config_file.endswith('.json'):
                    self.config = json.load(f)
                else:
                    raise ValueError("Unsupported config file format")
        except Exception as e:
            print(f"Error loading config file: {str(e)}")
            self.config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key (str): The configuration key.
            default (Any, optional): Default value if key is not found.

        Returns:
            Any: The configuration value.
        """
        return self.config.get(key, default)