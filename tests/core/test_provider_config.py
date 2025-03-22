# tests/core/test_provider_config.py
"""
Tests for the provider configuration service.
"""
import os
import json
import pytest
import tempfile
from src.core.provider_config import ProviderConfigService


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix=".json")
    
    # Write test configuration
    with os.fdopen(fd, 'w') as f:
        json.dump({
            "defaultProvider": "test-provider",
            "defaultModels": {
                "test-provider": "test-model",
                "other-provider": "other-model"
            },
            "providers": {
                "test-provider": {
                    "type": "test",
                    "apiKeyEnvVar": "TEST_API_KEY",
                    "baseUrl": "https://test.api",
                    "models": ["test-model", "test-model-2"],
                    "streaming": True
                },
                "other-provider": {
                    "type": "other",
                    "baseUrl": "http://other.api",
                    "models": ["other-model"],
                    "streaming": False
                }
            }
        }, f)
    
    yield path
    
    # Clean up
    os.unlink(path)


def test_load_config(temp_config_file):
    """Test loading configuration from file."""
    # Create config service with temp file
    config_service = ProviderConfigService(temp_config_file)
    
    # Verify config was loaded
    assert config_service.get_default_provider() == "test-provider"
    assert "test-provider" in config_service.get_all_providers()
    assert "other-provider" in config_service.get_all_providers()
    
    # Verify provider config
    provider_config = config_service.get_provider_config("test-provider")
    assert provider_config["type"] == "test"
    assert provider_config["baseUrl"] == "https://test.api"
    assert len(provider_config["models"]) == 2


def test_load_nonexistent_config():
    """Test loading a non-existent config file."""
    # Create config service with non-existent file
    config_service = ProviderConfigService("nonexistent.json")
    
    # Verify default config was created
    assert config_service.get_default_provider() == "openai"
    assert "openai" in config_service.get_all_providers()
    assert "ollama" in config_service.get_all_providers()


def test_get_default_model(temp_config_file):
    """Test getting the default model for a provider."""
    config_service = ProviderConfigService(temp_config_file)
    
    assert config_service.get_default_model("test-provider") == "test-model"
    assert config_service.get_default_model("other-provider") == "other-model"
    assert config_service.get_default_model("unknown-provider") is None


def test_add_provider(temp_config_file):
    """Test adding a provider configuration."""
    config_service = ProviderConfigService(temp_config_file)
    
    # Add a new provider
    success = config_service.add_provider("new-provider", {
        "type": "new",
        "baseUrl": "https://new.api",
        "models": ["new-model"],
        "streaming": True
    })
    
    assert success
    
    # Verify it was added
    providers = config_service.get_all_providers()
    assert "new-provider" in providers
    assert providers["new-provider"]["type"] == "new"
    
    # Verify it was saved to the file
    with open(temp_config_file, 'r') as f:
        saved_config = json.load(f)
        assert "new-provider" in saved_config["providers"]


def test_remove_provider(temp_config_file):
    """Test removing a provider configuration."""
    config_service = ProviderConfigService(temp_config_file)
    
    # Remove a provider
    success = config_service.remove_provider("other-provider")
    
    assert success
    
    # Verify it was removed
    providers = config_service.get_all_providers()
    assert "other-provider" not in providers
    assert "test-provider" in providers
    
    # Verify it was removed from defaultModels
    with open(temp_config_file, 'r') as f:
        saved_config = json.load(f)
        assert "other-provider" not in saved_config["defaultModels"]


def test_remove_default_provider(temp_config_file):
    """Test removing the default provider."""
    config_service = ProviderConfigService(temp_config_file)
    
    # Remove the default provider
    success = config_service.remove_provider("test-provider")
    
    assert success
    
    # Verify the default provider was updated
    assert config_service.get_default_provider() == "other-provider"
    
    # Verify it was saved to the file
    with open(temp_config_file, 'r') as f:
        saved_config = json.load(f)
        assert saved_config["defaultProvider"] == "other-provider"


def test_update_provider(temp_config_file):
    """Test updating a provider configuration."""
    config_service = ProviderConfigService(temp_config_file)
    
    # Update a provider
    success = config_service.update_provider("test-provider", {
        "type": "updated",
        "baseUrl": "https://updated.api",
        "models": ["updated-model"],
        "streaming": False
    })
    
    assert success
    
    # Verify it was updated
    provider_config = config_service.get_provider_config("test-provider")
    assert provider_config["type"] == "updated"
    assert provider_config["baseUrl"] == "https://updated.api"
    assert provider_config["models"] == ["updated-model"]
    assert provider_config["streaming"] == False
    
    # Verify it was saved to the file
    with open(temp_config_file, 'r') as f:
        saved_config = json.load(f)
        assert saved_config["providers"]["test-provider"]["type"] == "updated"


def test_set_default_provider(temp_config_file):
    """Test setting the default provider."""
    config_service = ProviderConfigService(temp_config_file)
    
    # Set the default provider
    success = config_service.set_default_provider("other-provider")
    
    assert success
    assert config_service.get_default_provider() == "other-provider"
    
    # Verify it was saved to the file
    with open(temp_config_file, 'r') as f:
        saved_config = json.load(f)
        assert saved_config["defaultProvider"] == "other-provider"


def test_set_default_model(temp_config_file):
    """Test setting the default model for a provider."""
    config_service = ProviderConfigService(temp_config_file)
    
    # Set the default model
    success = config_service.set_default_model("test-provider", "test-model-2")
    
    assert success
    assert config_service.get_default_model("test-provider") == "test-model-2"
    
    # Verify it was saved to the file
    with open(temp_config_file, 'r') as f:
        saved_config = json.load(f)
        assert saved_config["defaultModels"]["test-provider"] == "test-model-2"


def test_get_api_key(temp_config_file, monkeypatch):
    """Test getting the API key for a provider."""
    config_service = ProviderConfigService(temp_config_file)
    
    # Set environment variable
    monkeypatch.setenv("TEST_API_KEY", "test-key-value")
    
    # Get API key
    api_key = config_service.get_api_key("test-provider")
    
    assert api_key == "test-key-value"
    
    # Test provider without API key
    api_key = config_service.get_api_key("other-provider")
    
    assert api_key is None


def test_get_models(temp_config_file):
    """Test getting the models for a provider."""
    config_service = ProviderConfigService(temp_config_file)
    
    # Get models
    models = config_service.get_models("test-provider")
    
    assert models == ["test-model", "test-model-2"]
    
    # Test unknown provider
    models = config_service.get_models("unknown-provider")
    
    assert models == []
