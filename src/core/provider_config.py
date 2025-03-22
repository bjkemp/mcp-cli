# src/core/provider_config.py
"""
Provider Configuration Service for MCP-CLI.

This module manages the configuration of LLM providers, including
API keys, models, and provider-specific settings.
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path


class ProviderConfigService:
    """Service for managing provider configuration."""
    
    def __init__(self, config_file: str = "providers_config.json"):
        """
        Initialize the provider configuration service.
        
        Args:
            config_file: Path to the provider configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dict containing provider configuration data
        """
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Error loading provider config file {self.config_file}: {str(e)}")
            # Return default configuration if file not found or invalid
            return {
                "defaultProvider": "openai",
                "defaultModels": {
                    "openai": "gpt-4o-mini",
                    "ollama": "llama3.2"
                },
                "providers": {
                    "openai": {
                        "type": "openai",
                        "apiKeyEnvVar": "OPENAI_API_KEY",
                        "baseUrl": "https://api.openai.com/v1",
                        "models": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                        "streaming": True
                    },
                    "ollama": {
                        "type": "ollama",
                        "baseUrl": "http://localhost:11434",
                        "models": ["llama3.2", "qwen2.5-coder", "llama3"],
                        "streaming": True
                    }
                }
            }
            
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error saving provider config file {self.config_file}: {str(e)}")
            return False
            
    def get_default_provider(self) -> str:
        """
        Get the default provider name.
        
        Returns:
            Default provider name
        """
        return self.config.get("defaultProvider", "openai")
        
    def get_default_model(self, provider: str) -> Optional[str]:
        """
        Get the default model for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Default model name or None if not set
        """
        return self.config.get("defaultModels", {}).get(provider)
        
    def get_provider_config(self, provider: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Provider configuration or None if not found
        """
        return self.config.get("providers", {}).get(provider)
        
    def get_all_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available provider configurations.
        
        Returns:
            Dict of provider configurations
        """
        return self.config.get("providers", {})
        
    def add_provider(self, name: str, config: Dict[str, Any]) -> bool:
        """
        Add a new provider configuration.
        
        Args:
            name: Provider name
            config: Provider configuration
            
        Returns:
            True if successful, False otherwise
        """
        if "providers" not in self.config:
            self.config["providers"] = {}
            
        self.config["providers"][name] = config
        return self.save_config()
        
    def remove_provider(self, name: str) -> bool:
        """
        Remove a provider configuration.
        
        Args:
            name: Provider name
            
        Returns:
            True if successful, False otherwise
        """
        if name in self.config.get("providers", {}):
            del self.config["providers"][name]
            
            # Remove from default models if present
            if name in self.config.get("defaultModels", {}):
                del self.config["defaultModels"][name]
                
            # Change default provider if needed
            if self.config.get("defaultProvider") == name:
                providers = list(self.config.get("providers", {}).keys())
                self.config["defaultProvider"] = providers[0] if providers else "openai"
                
            return self.save_config()
        return False
        
    def update_provider(self, name: str, config: Dict[str, Any]) -> bool:
        """
        Update an existing provider configuration.
        
        Args:
            name: Provider name
            config: New provider configuration
            
        Returns:
            True if successful, False otherwise
        """
        if name in self.config.get("providers", {}):
            self.config["providers"][name] = config
            return self.save_config()
        return False
        
    def set_default_provider(self, name: str) -> bool:
        """
        Set the default provider.
        
        Args:
            name: Provider name
            
        Returns:
            True if successful, False otherwise
        """
        if name in self.config.get("providers", {}):
            self.config["defaultProvider"] = name
            return self.save_config()
        return False
        
    def set_default_model(self, provider: str, model: str) -> bool:
        """
        Set the default model for a provider.
        
        Args:
            provider: Provider name
            model: Model name
            
        Returns:
            True if successful, False otherwise
        """
        if provider in self.config.get("providers", {}):
            if "defaultModels" not in self.config:
                self.config["defaultModels"] = {}
                
            self.config["defaultModels"][provider] = model
            return self.save_config()
        return False
        
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get the API key for a provider from environment variables.
        
        Args:
            provider: Provider name
            
        Returns:
            API key or None if not found
        """
        provider_config = self.get_provider_config(provider)
        if not provider_config:
            return None
            
        api_key_var = provider_config.get("apiKeyEnvVar")
        if not api_key_var:
            return None
            
        return os.environ.get(api_key_var)
        
    def get_models(self, provider: str) -> List[str]:
        """
        Get the list of models for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            List of model names
        """
        provider_config = self.get_provider_config(provider)
        if not provider_config:
            return []
            
        return provider_config.get("models", [])
