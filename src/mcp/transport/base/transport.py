# src/mcp/transport/base/transport.py
"""
Base transport interface for MCP protocol.

This module defines the abstract Transport interface that all transport
implementations must follow.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, AsyncGenerator, Union


class Transport(ABC):
    """Base class for MCP transports."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the server.
        
        Returns:
            True if connected successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the server.
        
        Returns:
            True if disconnected successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def send_message(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to the server and get the response.
        
        Args:
            method: The method name to call
            params: Parameters for the method
            
        Returns:
            The response from the server
            
        Raises:
            TransportError: If an error occurs during transport
        """
        pass
    
    @abstractmethod
    async def send_streaming_message(self, method: str, params: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Send a message to the server and get a streaming response.
        
        Args:
            method: The method name to call
            params: Parameters for the method
            
        Returns:
            An async generator yielding response chunks
            
        Raises:
            TransportError: If an error occurs during transport
        """
        pass


class TransportError(Exception):
    """Error raised when a transport error occurs."""
    
    def __init__(self, message: str, cause: Optional[Exception] = None):
        """
        Initialize a new transport error.
        
        Args:
            message: Error message
            cause: The underlying cause (optional)
        """
        self.message = message
        self.cause = cause
        super().__init__(message)
