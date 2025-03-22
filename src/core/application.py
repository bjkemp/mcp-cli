# src/core/application.py
"""
Core Application class for MCP-CLI.

The Application class serves as the main entry point and coordinates
all the components of the application.
"""
import asyncio
import sys
import atexit
import os
import signal
import logging
from typing import Dict, List, Optional, Any

from core.di import Container
from core.services import ServiceRegistry
from core.errors import MCPError, ErrorHandler


class Application:
    """Core application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.running = True
        self.logger = logging.getLogger("mcp-cli")
    
    async def initialize(self, config_file: str = "server_config.json") -> bool:
        """
        Initialize the application.
        
        Args:
            config_file: Path to the server configuration file
            
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Register services
            self._register_services(config_file)
            
            # Setup signal handlers and exit handlers
            self.setup_signal_handlers()
            self.register_exit_handlers()
            
            self.logger.info("Application initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {str(e)}")
            return False
            
    def _register_services(self, config_file: str) -> None:
        """
        Register application services.
        
        Args:
            config_file: Path to the server configuration file
        """
        # Register core services
        ServiceRegistry.register_services()
        
        # Register factories for lazy-loaded services
        ServiceRegistry.register_factories()
        
        # Configure the server config service
        config_service = Container.resolve('config_service')
        if config_file != "server_config.json":
            config_service.config_file = config_file
            config_service.config = config_service._load_config()
    
    def setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(sig, frame):
            self.logger.info(f"Received signal {sig}")
            self.running = False
            asyncio.create_task(self.shutdown())
            
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # On non-Windows platforms, handle SIGQUIT
        if hasattr(signal, 'SIGQUIT'):
            signal.signal(signal.SIGQUIT, signal_handler)
            
    def register_exit_handlers(self) -> None:
        """Register exit handlers."""
        def exit_handler():
            # Restore terminal
            os.system("stty sane")
            
            # Clean up any resources that need synchronous shutdown
            self.logger.info("Application shutdown in exit handler")
                
        atexit.register(exit_handler)
        
    async def shutdown(self) -> None:
        """Shutdown the application."""
        self.logger.info("Shutting down application")
        
        # Get the server service if it exists
        try:
            server_service = Container.resolve('server_service')
            await server_service.stop_all_servers()
        except KeyError:
            # Server service not registered yet
            pass
        
        # Force exit after cleanup
        sys.exit(0)
    
    @staticmethod
    def handle_error(error: Exception) -> str:
        """
        Handle an exception and return a formatted error message.
        
        Args:
            error: The exception to handle
            
        Returns:
            Formatted error message
        """
        return ErrorHandler.format_error(error)
