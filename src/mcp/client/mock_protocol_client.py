# src/mcp/client/mock_protocol_client.py
"""
Mock implementation of the MCP protocol client for testing.

This module provides a mock implementation of the ProtocolClient
interface for testing without a real MCP server.
"""
import logging
from typing import Any, Dict, List, Optional, AsyncGenerator

from mcp.client.protocol_client import ProtocolClient
from mcp.messages.exceptions import (
    MCPProtocolError, 
    InvalidToolError, 
    ToolExecutionError
)


class MockProtocolClient(ProtocolClient):
    """Mock MCP protocol client for testing."""
    
    def __init__(self):
        """Initialize the mock protocol client."""
        self.capabilities = {
            "tools": [],
            "prompts": [],
            "resources": []
        }
        self.tool_results = {}
        self.streaming_tool_results = {}
        self.prompt_results = {}
        self.resource_results = {}
        self.connected = False
        self.logger = logging.getLogger("mcp-cli.mock-protocol-client")
    
    def set_capabilities(self, capabilities: Dict[str, Any]) -> None:
        """
        Set the capabilities to return.
        
        Args:
            capabilities: The capabilities to return
        """
        self.capabilities = capabilities
    
    def add_tool(self, tool_def: Dict[str, Any]) -> None:
        """
        Add a tool to the capabilities.
        
        Args:
            tool_def: The tool definition
        """
        if "tools" not in self.capabilities:
            self.capabilities["tools"] = []
        
        self.capabilities["tools"].append(tool_def)
    
    def add_prompt(self, prompt_def: Dict[str, Any]) -> None:
        """
        Add a prompt to the capabilities.
        
        Args:
            prompt_def: The prompt definition
        """
        if "prompts" not in self.capabilities:
            self.capabilities["prompts"] = []
        
        self.capabilities["prompts"].append(prompt_def)
    
    def add_resource(self, resource_def: Dict[str, Any]) -> None:
        """
        Add a resource to the capabilities.
        
        Args:
            resource_def: The resource definition
        """
        if "resources" not in self.capabilities:
            self.capabilities["resources"] = []
        
        self.capabilities["resources"].append(resource_def)
    
    def set_tool_result(self, tool_name: str, params_hash: str, result: Any) -> None:
        """
        Set the result for a specific tool call.
        
        Args:
            tool_name: Name of the tool
            params_hash: Hash of the parameters
            result: The result to return
        """
        if tool_name not in self.tool_results:
            self.tool_results[tool_name] = {}
        
        self.tool_results[tool_name][params_hash] = result
    
    def set_streaming_tool_result(self, tool_name: str, params_hash: str, results: List[Any]) -> None:
        """
        Set the streaming result for a specific tool call.
        
        Args:
            tool_name: Name of the tool
            params_hash: Hash of the parameters
            results: The list of results to return
        """
        if tool_name not in self.streaming_tool_results:
            self.streaming_tool_results[tool_name] = {}
        
        self.streaming_tool_results[tool_name][params_hash] = results
    
    def set_prompt_result(self, prompt_name: str, params_hash: str, result: Any) -> None:
        """
        Set the result for a specific prompt.
        
        Args:
            prompt_name: Name of the prompt
            params_hash: Hash of the parameters
            result: The result to return
        """
        if prompt_name not in self.prompt_results:
            self.prompt_results[prompt_name] = {}
        
        self.prompt_results[prompt_name][params_hash] = result
    
    def set_resource_result(self, resource_name: str, params_hash: str, result: Any) -> None:
        """
        Set the result for a specific resource.
        
        Args:
            resource_name: Name of the resource
            params_hash: Hash of the parameters
            result: The result to return
        """
        if resource_name not in self.resource_results:
            self.resource_results[resource_name] = {}
        
        self.resource_results[resource_name][params_hash] = result
    
    def _hash_params(self, params: Optional[Dict[str, Any]]) -> str:
        """
        Create a simple hash for parameters.
        
        Args:
            params: The parameters to hash
            
        Returns:
            A string hash of the parameters
        """
        if not params:
            return "empty"
        
        # For testing purposes, we can use a simple string representation
        return str(sorted(params.items()))
    
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize the connection and get capabilities.
        
        Returns:
            The server capabilities
            
        Raises:
            ProtocolError: If initialization fails
        """
        self.connected = True
        return self.capabilities
    
    async def ping(self) -> bool:
        """
        Ping the server to check if it's responsive.
        
        Returns:
            True if the server is responsive, False otherwise
        """
        return self.connected
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get available tools from the server.
        
        Returns:
            List of tool definitions
            
        Raises:
            ProtocolError: If an error occurs
        """
        return self.capabilities.get("tools", [])
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the server.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
            
        Returns:
            The tool execution result
            
        Raises:
            InvalidToolError: If the tool is not valid
            ToolExecutionError: If an error occurs during tool execution
        """
        # Check if tool exists
        if not any(tool["name"] == tool_name for tool in self.capabilities.get("tools", [])):
            raise InvalidToolError(tool_name)
        
        # Get the result
        params_hash = self._hash_params(params)
        
        if tool_name in self.tool_results and params_hash in self.tool_results[tool_name]:
            result = self.tool_results[tool_name][params_hash]
            
            # If the result is an exception, raise it
            if isinstance(result, Exception):
                raise result
            
            return result
        
        # Default result
        return {"result": f"Mock result for {tool_name}"}
    
    async def call_streaming_tool(self, tool_name: str, params: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Call a tool on the server with streaming response.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
            
        Returns:
            An async generator yielding result chunks
            
        Raises:
            InvalidToolError: If the tool is not valid
            ToolExecutionError: If an error occurs during tool execution
        """
        # Check if tool exists
        if not any(tool["name"] == tool_name for tool in self.capabilities.get("tools", [])):
            raise InvalidToolError(tool_name)
        
        # Get the result
        params_hash = self._hash_params(params)
        
        if tool_name in self.streaming_tool_results and params_hash in self.streaming_tool_results[tool_name]:
            results = self.streaming_tool_results[tool_name][params_hash]
            
            # Yield each result
            for result in results:
                # If the result is an exception, raise it
                if isinstance(result, Exception):
                    raise result
                
                yield result
            
            return
        
        # Default result
        yield {"result": f"Mock streaming result for {tool_name}"}
    
    async def get_prompts(self) -> List[Dict[str, Any]]:
        """
        Get available prompts from the server.
        
        Returns:
            List of prompt definitions
            
        Raises:
            ProtocolError: If an error occurs
        """
        return self.capabilities.get("prompts", [])
    
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
        # Check if prompt exists
        if not any(prompt["name"] == prompt_name for prompt in self.capabilities.get("prompts", [])):
            raise MCPProtocolError(f"Prompt not found: {prompt_name}", 1201)
        
        # Get the result
        params_hash = self._hash_params(params)
        
        if prompt_name in self.prompt_results and params_hash in self.prompt_results[prompt_name]:
            result = self.prompt_results[prompt_name][params_hash]
            
            # If the result is an exception, raise it
            if isinstance(result, Exception):
                raise result
            
            return result
        
        # Default result
        return {"content": f"Mock prompt content for {prompt_name}"}
    
    async def get_resources(self) -> List[Dict[str, Any]]:
        """
        Get available resources from the server.
        
        Returns:
            List of resource definitions
            
        Raises:
            ProtocolError: If an error occurs
        """
        return self.capabilities.get("resources", [])
    
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
        # Check if resource exists
        if not any(resource["name"] == resource_name for resource in self.capabilities.get("resources", [])):
            raise MCPProtocolError(f"Resource not found: {resource_name}", 1301)
        
        # Get the result
        params_hash = self._hash_params(params)
        
        if resource_name in self.resource_results and params_hash in self.resource_results[resource_name]:
            result = self.resource_results[resource_name][params_hash]
            
            # If the result is an exception, raise it
            if isinstance(result, Exception):
                raise result
            
            return result
        
        # Default result
        return {"content": f"Mock resource content for {resource_name}"}
    
    async def shutdown(self) -> bool:
        """
        Shutdown the connection.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        self.connected = False
        return True
