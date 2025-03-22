# tests/core/test_di.py
"""
Tests for the dependency injection container.
"""
import pytest
from src.core.di import Container


def test_register_and_resolve():
    """Test registering and resolving an implementation."""
    # Clear container before test
    Container.clear()
    
    # Create a test implementation
    class TestService:
        def __init__(self):
            self.value = 42
    
    # Register the implementation
    test_service = TestService()
    Container.register("test_service", test_service)
    
    # Resolve the implementation
    resolved = Container.resolve("test_service")
    
    # Verify it's the same instance
    assert resolved is test_service
    assert resolved.value == 42


def test_register_factory():
    """Test registering and resolving a factory."""
    # Clear container before test
    Container.clear()
    
    # Create a test factory
    factory_called = False
    
    def factory():
        nonlocal factory_called
        factory_called = True
        return {"name": "Test"}
    
    # Register the factory
    Container.register("test_factory", factory=factory)
    
    # Verify factory not called yet
    assert not factory_called
    
    # Resolve the implementation
    resolved = Container.resolve("test_factory")
    
    # Verify factory was called
    assert factory_called
    assert resolved["name"] == "Test"
    
    # Verify subsequent resolves return the same instance
    resolved2 = Container.resolve("test_factory")
    assert resolved2 is resolved


def test_resolve_unknown():
    """Test resolving an unknown interface."""
    # Clear container before test
    Container.clear()
    
    # Attempt to resolve an unknown interface
    with pytest.raises(KeyError):
        Container.resolve("unknown_service")


def test_multiple_registrations():
    """Test registering multiple implementations."""
    # Clear container before test
    Container.clear()
    
    # Register multiple implementations
    Container.register("service1", "Implementation 1")
    Container.register("service2", "Implementation 2")
    
    # Resolve both implementations
    assert Container.resolve("service1") == "Implementation 1"
    assert Container.resolve("service2") == "Implementation 2"


def test_override_registration():
    """Test overriding a registration."""
    # Clear container before test
    Container.clear()
    
    # Register an implementation
    Container.register("service", "Original")
    
    # Override it
    Container.register("service", "Override")
    
    # Resolve the implementation
    assert Container.resolve("service") == "Override"
