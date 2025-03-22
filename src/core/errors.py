# src/core/errors.py
"""
Error handling system for MCP-CLI.

This module defines standard error types and error handling utilities
for consistent error management throughout the application.
"""
from typing import Dict, Optional, Any


class MCPError(Exception):
    """Base class for all MCP-CLI errors."""
    
    def __init__(self, message: str, code: int = 1, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a new MCP error.
        
        Args:
            message: Error message
            code: Error code
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class ConfigurationError(MCPError):
    """Error raised when there is a problem with configuration."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 100, details)


class ProviderError(MCPError):
    """Error raised when there is a problem with a provider."""
    
    def __init__(self, message: str, provider: str, details: Optional[Dict[str, Any]] = None):
        details_with_provider = {'provider': provider, **(details or {})}
        super().__init__(message, 200, details_with_provider)


class ProtocolError(MCPError):
    """Error raised when there is a problem with the MCP protocol."""
    
    def __init__(self, message: str, method: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details_with_method = {'method': method, **(details or {})} if method else details
        super().__init__(message, 300, details_with_method)


class ServerError(MCPError):
    """Error raised when there is a problem with an MCP server."""
    
    def __init__(self, message: str, server: str, details: Optional[Dict[str, Any]] = None):
        details_with_server = {'server': server, **(details or {})}
        super().__init__(message, 400, details_with_server)


class ToolError(MCPError):
    """Error raised when there is a problem executing a tool."""
    
    def __init__(self, message: str, tool: str, details: Optional[Dict[str, Any]] = None):
        details_with_tool = {'tool': tool, **(details or {})}
        super().__init__(message, 500, details_with_tool)


class ErrorHandler:
    """Utility class for handling errors."""
    
    @staticmethod
    def format_error(error: Exception) -> str:
        """
        Format an error for display.
        
        Args:
            error: The exception to format
            
        Returns:
            Formatted error message
        """
        if isinstance(error, MCPError):
            # Format MCP errors with code and details if available
            if error.details:
                details_str = ', '.join(f"{k}={v}" for k, v in error.details.items())
                return f"Error [{error.code}]: {error.message} ({details_str})"
            else:
                return f"Error [{error.code}]: {error.message}"
        else:
            # Format standard exceptions
            return f"Error: {str(error)}"
