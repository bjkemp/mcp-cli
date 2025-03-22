# src/mcp/client/protocol_client.py
"""
MCP protocol client interface.

This module defines the abstract ProtocolClient interface that all
protocol client implementations must follow.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator


class ProtocolClient(ABC):
    """Base class for MCP protocol clients."""
    
    @abstractmethod
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize the connection and get capabilities.
        
        Returns:
            The server capabilities
            
        Raises:
            ProtocolError: If initialization fails
        """
        pass
    
    @abstractmethod
    async def ping(self) -> bool:
        """
        Ping the server to check if it's responsive.
        
        Returns:
            True if the server is responsive, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get available tools from the server.
        
        Returns:
            List of tool definitions
            
        Raises:
            ProtocolError: If an error occurs
        """
        pass
    
    @abstractmethod
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the server.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
            
        Returns:
            The tool execution result
            
        Raises:
            ProtocolError: If an error occurs during tool execution
        """
        pass
    
    @abstractmethod
    async def call_streaming_tool(self, tool_name: str, params: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Call a tool on the server with streaming response.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
            
        Returns:
            An async generator yielding result chunks
            
        Raises:
            ProtocolError: If an error occurs during tool execution
        """
        pass
    
    @abstractmethod
    async def get_prompts(self) -> List[Dict[str, Any]]:
        """
        Get available prompts from the server.
        
        Returns:
            List of prompt definitions
            
        Raises:
            ProtocolError: If an error occurs
        """
        pass
    
    @abstractmethod
    async def get_prompt(self, prompt_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get a specific prompt from the server.
        
        Args:
            prompt_name: Name of the prompt to get
            params: Parameters for the prompt (optional)
            
        Returns:
            The prompt content
            
        Raises:
            ProtocolError: If an error occurs
        """
        pass
    
    @abstractmethod
    async def get_resources(self) -> List[Dict[str, Any]]:
        """
        Get available resources from the server.
        
        Returns:
            List of resource definitions
            
        Raises:
            ProtocolError: If an error occurs
        """
        pass
    
    @abstractmethod
    async def get_resource(self, resource_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get a specific resource from the server.
        
        Args:
            resource_name: Name of the resource to get
            params: Parameters for the resource (optional)
            
        Returns:
            The resource content
            
        Raises:
            ProtocolError: If an error occurs
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """
        Shutdown the connection.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        pass
