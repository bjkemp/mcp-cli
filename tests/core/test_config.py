# tests/core/test_config.py
"""
Tests for the configuration service.
"""
import os
import json
import pytest
import tempfile
from src.core.config import ConfigService


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix=".json")
    
    # Write test configuration
    with os.fdopen(fd, 'w') as f:
        json.dump({
            "mcpServers": {
                "test1": {
                    "command": "test",
                    "args": ["--arg1", "--arg2"]
                },
                "test2": {
                    "command": "test2",
                    "args": []
                }
            }
        }, f)
    
    yield path
    
    # Clean up
    os.unlink(path)


def test_load_config(temp_config_file):
    """Test loading configuration from file."""
    # Create config service with temp file
    config_service = ConfigService(temp_config_file)
    
    # Verify config was loaded
    assert "mcpServers" in config_service.config
    assert "test1" in config_service.config["mcpServers"]
    assert "test2" in config_service.config["mcpServers"]
    
    # Verify server config
    server_config = config_service.get_server_config("test1")
    assert server_config["command"] == "test"
    assert "--arg1" in server_config["args"]


def test_load_nonexistent_config():
    """Test loading a non-existent config file."""
    # Create config service with non-existent file
    config_service = ConfigService("nonexistent.json")
    
    # Verify default config was created
    assert "mcpServers" in config_service.config
    assert isinstance(config_service.config["mcpServers"], dict)
    assert len(config_service.config["mcpServers"]) == 0


def test_get_all_servers(temp_config_file):
    """Test getting all server configurations."""
    config_service = ConfigService(temp_config_file)
    
    servers = config_service.get_all_servers()
    
    assert "test1" in servers
    assert "test2" in servers
    assert len(servers) == 2


def test_add_server(temp_config_file):
    """Test adding a server configuration."""
    config_service = ConfigService(temp_config_file)
    
    # Add a new server
    success = config_service.add_server("test3", {
        "command": "test3",
        "args": ["--verbose"]
    })
    
    assert success
    
    # Verify it was added
    servers = config_service.get_all_servers()
    assert "test3" in servers
    assert servers["test3"]["command"] == "test3"
    
    # Verify it was saved to the file
    with open(temp_config_file, 'r') as f:
        saved_config = json.load(f)
        assert "test3" in saved_config["mcpServers"]


def test_remove_server(temp_config_file):
    """Test removing a server configuration."""
    config_service = ConfigService(temp_config_file)
    
    # Remove a server
    success = config_service.remove_server("test1")
    
    assert success
    
    # Verify it was removed
    servers = config_service.get_all_servers()
    assert "test1" not in servers
    assert "test2" in servers
    
    # Verify it was saved to the file
    with open(temp_config_file, 'r') as f:
        saved_config = json.load(f)
        assert "test1" not in saved_config["mcpServers"]


def test_update_server(temp_config_file):
    """Test updating a server configuration."""
    config_service = ConfigService(temp_config_file)
    
    # Update a server
    success = config_service.update_server("test1", {
        "command": "updated",
        "args": ["--new-arg"]
    })
    
    assert success
    
    # Verify it was updated
    server_config = config_service.get_server_config("test1")
    assert server_config["command"] == "updated"
    assert "--new-arg" in server_config["args"]
    
    # Verify it was saved to the file
    with open(temp_config_file, 'r') as f:
        saved_config = json.load(f)
        assert saved_config["mcpServers"]["test1"]["command"] == "updated"
