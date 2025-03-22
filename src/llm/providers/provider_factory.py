# src/llm/providers/provider_factory.py
"""
Provider factory for LLM providers.

This module provides a factory for creating and managing LLM providers.
"""
import importlib
import inspect
import os
import logging
from typing import Dict, List, Optional, Type, Any

from llm.llm_client import LLMClient
from llm.providers.base import BaseProvider
from core.di import Container


class ProviderFactory:
    """Factory for creating and managing LLM providers."""
    
    def __init__(self):
        """Initialize the provider factory."""
        self._provider_types: Dict[str, Type[BaseProvider]] = {}
        self._provider_instances: Dict[str, BaseProvider] = {}
        self.logger = logging.getLogger("mcp-cli.provider-factory")
        
        # Register built-in providers
        self._register_builtin_providers()
    
    def _register_builtin_providers(self):
        """Register built-in provider types."""
        # Import the mock provider
        from llm.providers.mock_provider import MockProvider
        
        # Register provider type
        self.register_provider_type("mock", MockProvider)
        
        # Try to import other built-in providers
        try:
            # This will be implemented later
            pass
        except ImportError:
            # It's okay if some providers aren't available
            pass
        
        self.logger.info(f"Registered {len(self._provider_types)} built-in provider types")
    
    def register_provider_type(self, type_name: str, provider_class: Type[BaseProvider]) -> None:
        """
        Register a new provider type.
        
        Args:
            type_name: The type name of the provider
            provider_class: The provider class
        """
        self._provider_types[type_name] = provider_class
        self.logger.debug(f"Registered provider type: {type_name}")
    
    def create_provider(self, provider_name: str, model_name: Optional[str] = None) -> BaseProvider:
        """
        Create a provider instance based on configuration.
        
        Args:
            provider_name: Name of the provider configuration
            model_name: Name of the model to use (overrides default)
            
        Returns:
            A provider instance
            
        Raises:
            ValueError: If the provider is not found or cannot be created
        """
        # Get provider configuration
        try:
            config_service = Container.resolve('provider_config')
        except KeyError:
            raise ValueError("Provider configuration service not registered")
        
        provider_config = config_service.get_provider_config(provider_name)
        
        if not provider_config:
            raise ValueError(f"Provider '{provider_name}' not found in configuration")
        
        provider_type = provider_config.get("type")
        if provider_type not in self._provider_types:
            raise ValueError(f"Provider type '{provider_type}' not supported")
        
        # Use specified model or default
        if not model_name:
            model_name = config_service.get_default_model(provider_name)
        
        # Get API key if needed
        api_key = config_service.get_api_key(provider_name)
        
        # Create provider instance
        provider_class = self._provider_types[provider_type]
        
        # Prepare init parameters
        init_params = {
            "model_name": model_name,
            "base_url": provider_config.get("baseUrl"),
            "streaming": provider_config.get("streaming", True)
        }
        
        # Add API key if available
        if api_key:
            init_params["api_key"] = api_key
        
        # Add any additional options
        if "options" in provider_config:
            init_params.update(provider_config["options"])
        
        # Create instance with parameter filtering (only pass params that the __init__ accepts)
        sig = inspect.signature(provider_class.__init__)
        valid_params = {}
        for param_name, param in sig.parameters.items():
            if param_name != 'self' and param_name in init_params:
                valid_params[param_name] = init_params[param_name]
        
        provider = provider_class(**valid_params)
        
        # Cache instance
        self._provider_instances[provider_name] = provider
        
        self.logger.info(f"Created provider instance: {provider_name} ({provider_type})")
        return provider
    
    def get_provider(self, provider_name: str) -> Optional[BaseProvider]:
        """
        Get an existing provider instance.
        
        Args:
            provider_name: Name of the provider configuration
            
        Returns:
            The provider instance or None if not found
        """
        return self._provider_instances.get(provider_name)
    
    def get_available_provider_types(self) -> List[str]:
        """
        Get list of available provider types.
        
        Returns:
            List of provider type names
        """
        return list(self._provider_types.keys())
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of configured providers.
        
        Returns:
            List of provider configuration names
        """
        try:
            config_service = Container.resolve('provider_config')
            return list(config_service.get_all_providers().keys())
        except Exception:
            return []
    
    def load_custom_providers(self, directory: str = "custom_providers") -> int:
        """
        Load custom provider implementations from a directory.
        
        Args:
            directory: Path to the directory containing custom providers
            
        Returns:
            Number of provider types loaded
        """
        if not os.path.exists(directory):
            return 0
        
        count = 0
        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]  # Remove .py extension
                
                try:
                    # Import the module
                    spec = importlib.util.spec_from_file_location(
                        module_name, 
                        os.path.join(directory, filename)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find provider classes
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseProvider) and 
                            obj != BaseProvider):
                            
                            # Get provider type from class
                            provider_type = getattr(obj, "PROVIDER_TYPE", module_name)
                            
                            # Register the provider type
                            self.register_provider_type(provider_type, obj)
                            count += 1
                            
                except Exception as e:
                    self.logger.error(f"Error loading custom provider {module_name}: {str(e)}")
        
        if count > 0:
            self.logger.info(f"Loaded {count} custom provider types from {directory}")
        return count
