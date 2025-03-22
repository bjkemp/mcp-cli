# src/core/services.py
"""
Service Registry for MCP-CLI.

This module provides a centralized registry for application services,
making it easy to register and manage all services in one place.
"""
from typing import Any, Dict, Optional
from core.di import Container


class ServiceRegistry:
    """Registry for application services."""
    
    @classmethod
    def register_services(cls) -> None:
        """Register all application services."""
        # Import services here to avoid circular imports
        from core.config import ConfigService
        from core.provider_config import ProviderConfigService
        
        # Create and register services
        config_service = ConfigService()
        provider_config_service = ProviderConfigService()
        
        # Register in the container
        Container.register('config_service', config_service)
        Container.register('provider_config', provider_config_service)
        
    @classmethod
    def register_factories(cls) -> None:
        """Register all factory methods for lazily created services."""
        # These imports will be added as we create the respective modules
        # This method will be expanded in future phases
        pass
