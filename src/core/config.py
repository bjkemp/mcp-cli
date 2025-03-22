# src/core/config.py
"""
Configuration Service for MCP-CLI.

This module provides functionality for loading, accessing, and managing
application configuration from various sources.
"""
import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConfigService:
    """Service for managing application configuration."""
    
    def __init__(self, config_file: str = "server_config.json"):
        """
        Initialize the configuration service.
        
        Args:
            config_file: Path to the main configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dict containing configuration data
        """
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Error loading config file {self.config_file}: {str(e)}")
            # Return empty default configuration
            return {"mcpServers": {}}
    
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
            logging.error(f"Error saving config file {self.config_file}: {str(e)}")
            return False
    
    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            Server configuration or None if not found
        """
        return self.config.get("mcpServers", {}).get(server_name)
    
    def get_all_servers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available server configurations.
        
        Returns:
            Dict of server configurations
        """
        return self.config.get("mcpServers", {})
    
    def add_server(self, name: str, config: Dict[str, Any]) -> bool:
        """
        Add a new server configuration.
        
        Args:
            name: Server name
            config: Server configuration
            
        Returns:
            True if successful, False otherwise
        """
        if "mcpServers" not in self.config:
            self.config["mcpServers"] = {}
            
        self.config["mcpServers"][name] = config
        return self.save_config()
    
    def remove_server(self, name: str) -> bool:
        """
        Remove a server configuration.
        
        Args:
            name: Server name
            
        Returns:
            True if successful, False otherwise
        """
        if name in self.config.get("mcpServers", {}):
            del self.config["mcpServers"][name]
            return self.save_config()
        return False
    
    def update_server(self, name: str, config: Dict[str, Any]) -> bool:
        """
        Update an existing server configuration.
        
        Args:
            name: Server name
            config: New server configuration
            
        Returns:
            True if successful, False otherwise
        """
        if name in self.config.get("mcpServers", {}):
            self.config["mcpServers"][name] = config
            return self.save_config()
        return False
