import os
import yaml
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger()

class ConfigManager:
    # Default values
    DEFAULT_CONFIG = {
        "lm_studio_completions_url": "http://localhost:1234/v1/chat/completions",
        "llm_model": "llama-3.2-3b-instruct",
        "whisper_model_type": "base",
        "wake_words": "jarvis",
        "temperature": 0.7,
        "max_tokens": -1,
        "batch_size": 100,
        "max_vectors": 1000,
        "auto_save": True,
        "timeout": 30
    }

    DEFAULT_SECRETS = {
        "weather_api_key": None,
        "news_api_key": None
    }

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        self.secrets = self.DEFAULT_SECRETS.copy()
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration file"""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Config file not found: {self.config_path}")
                self._create_template()
                return

            with open(self.config_path, 'r') as file:
                yaml_config = yaml.safe_load(file)

            if not yaml_config:
                logger.error("Empty config file")
                return

            # Load config section
            if 'config' in yaml_config:
                loaded_config = {
                    key: value for item in yaml_config['config']
                    for key, value in item.items()
                }
                self.config.update(loaded_config)

            # Load secrets section
            if 'secrets' in yaml_config:
                loaded_secrets = {
                    key: value for item in yaml_config['secrets']
                    for key, value in item.items()
                }
                self.secrets.update(loaded_secrets)

            self._validate_config()

        except Exception as e:
            logger.error(f"Error loading config: {e}")

    def _create_template(self) -> None:
        """Create template config file"""
        try:
            template = {
                'config': [
                    {key: value} for key, value in self.DEFAULT_CONFIG.items()
                ],
                'secrets': [
                    {key: value if value else 'your_api_key'} 
                    for key, value in self.DEFAULT_SECRETS.items()
                ]
            }

            with open(self.config_path + '.template', 'w') as file:
                yaml.dump(template, file, default_flow_style=False)

            logger.info(f"Created config template: {self.config_path}.template")

        except Exception as e:
            logger.error(f"Error creating config template: {e}")

    def _validate_config(self) -> None:
        """Validate configuration values"""
        # Check LM Studio URL
        if not self.config['lm_studio_completions_url'].startswith(('http://', 'https://')):
            logger.warning("Invalid LM Studio URL format")
            self.config['lm_studio_completions_url'] = self.DEFAULT_CONFIG['lm_studio_completions_url']

        # Check model name
        if not isinstance(self.config['llm_model'], str):
            logger.warning("Invalid model name")
            self.config['llm_model'] = self.DEFAULT_CONFIG['llm_model']

        # Check numeric values
        self.config['temperature'] = float(self.config.get('temperature', 0.7))
        self.config['max_tokens'] = int(self.config.get('max_tokens', -1))
        self.config['batch_size'] = max(1, int(self.config.get('batch_size', 100)))
        self.config['max_vectors'] = max(1, int(self.config.get('max_vectors', 1000)))
        self.config['timeout'] = max(1, int(self.config.get('timeout', 30)))

        # Check API keys
        for key in self.secrets:
            if not self.secrets[key] or self.secrets[key] == 'your_api_key':
                logger.warning(f"Missing or invalid API key: {key}")

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def get_secret(self, key: str, default: Any = None) -> Any:
        """Get secret value"""
        return self.secrets.get(key, default)

    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration"""
        return {
            'config': self.config,
            'secrets': self.secrets
        }

# Global config instance
_config_manager: Optional[ConfigManager] = None

def get_config_manager() -> ConfigManager:
    """Get global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

# Export
export = {
    'get_config_manager': get_config_manager
}