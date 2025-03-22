# src/core/di.py
"""
Dependency Injection Container for MCP-CLI.

This module provides a simple dependency injection container that allows for
registering and resolving dependencies throughout the application.
"""
from typing import Any, Callable, Dict, Optional, Type


class Container:
    """Simple dependency injection container."""
    
    _instances: Dict[str, Any] = {}
    _factories: Dict[str, Callable[[], Any]] = {}
    
    @classmethod
    def register(cls, interface: str, implementation: Any = None, factory: Optional[Callable[[], Any]] = None) -> None:
        """
        Register an implementation for an interface.
        
        Args:
            interface: The name of the interface/service
            implementation: The implementation instance (if not using a factory)
            factory: A factory function that creates the implementation
        """
        if factory:
            cls._factories[interface] = factory
        else:
            cls._instances[interface] = implementation
    
    @classmethod
    def resolve(cls, interface: str) -> Any:
        """
        Resolve an implementation for an interface.
        
        Args:
            interface: The name of the interface/service to resolve
            
        Returns:
            The implementation instance
            
        Raises:
            KeyError: If the interface is not registered
        """
        if interface in cls._factories:
            # If we haven't created this factory's instance yet, create and store it
            if interface not in cls._instances:
                cls._instances[interface] = cls._factories[interface]()
            return cls._instances[interface]
        elif interface in cls._instances:
            return cls._instances[interface]
        else:
            raise KeyError(f"No implementation registered for interface: {interface}")
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registrations (useful for testing)."""
        cls._instances.clear()
        cls._factories.clear()
