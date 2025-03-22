# src/mcp/client/standard_protocol_client.py
"""
Standard implementation of the MCP protocol client.

This module provides a standard implementation of the ProtocolClient
interface for MCP servers.
"""
import logging
from typing import Any, Dict, List, Optional, AsyncGenerator

from mcp.client.protocol_client import ProtocolClient
from mcp.transport.base.transport import Transport, TransportError
from mcp.messages.message_method import MessageMethod
from mcp.messages.exceptions import (
    MCPProtocolError, 
    InitializationError, 
    InvalidToolError, 
    ToolExecutionError
)


class StandardProtocolClient(ProtocolClient):
    """Standard implementation of the MCP protocol client."""
    
    def __init__(self, transport: Transport):
        """
        Initialize the standard protocol client.
        
        Args:
            transport: The transport to use for communication
        """
        self.transport = transport
        self.capabilities = None
        self.logger = logging.getLogger("mcp-cli.protocol-client")
    
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize the connection and get capabilities.
        
        Returns:
            The server capabilities
            
        Raises:
            InitializationError: If initialization fails
        """
        try:
            # Connect to the server
            success = await self.transport.connect()
            if not success:
                raise InitializationError("Failed to connect to server")
            
            # Send initialize message
            response = await self.transport.send_message(
                MessageMethod.INITIALIZE,
                {
                    "clientInfo": {
                        "name": "mcp-cli",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": True,
                        "prompts": True,
                        "resources": True
                    }
                }
            )
            
            if "result" in response:
                self.capabilities = response["result"]
                return self.capabilities
            else:
                # Handle error response
                if "error" in response:
                    error = response["error"]
                    raise InitializationError(
                        error.get("message", "Unknown initialization error"),
                        error.get("data")
                    )
                else:
                    raise InitializationError("Invalid response from server")
                
        except TransportError as e:
            raise InitializationError(f"Transport error: {e.message}", {"cause": str(e.cause) if e.cause else None})
        except Exception as e:
            if not isinstance(e, MCPProtocolError):
                raise InitializationError(f"Unexpected error: {str(e)}")
            raise
    
    async def ping(self) -> bool:
        """
        Ping the server to check if it's responsive.
        
        Returns:
            True if the server is responsive, False otherwise
        """
        try:
            response = await self.transport.send_message(MessageMethod.PING, {})
            return "result" in response
        except Exception as e:
            self.logger.warning(f"Ping failed: {str(e)}")
            return False
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get available tools from the server.
        
        Returns:
            List of tool definitions
            
        Raises:
            ProtocolError: If an error occurs
        """
        try:
            response = await self.transport.send_message(MessageMethod.TOOLS_LIST, {})
            
            if "result" in response:
                return response["result"].get("tools", [])
            else:
                # Handle error response
                if "error" in response:
                    error = response["error"]
                    raise MCPProtocolError(
                        error.get("message", "Unknown error"),
                        error.get("code", 0),
                        error.get("data")
                    )
                else:
                    return []
                
        except TransportError as e:
            raise MCPProtocolError(f"Transport error: {e.message}", 0, {"cause": str(e.cause) if e.cause else None})
    
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
        try:
            response = await self.transport.send_message(
                MessageMethod.TOOLS_CALL,
                {
                    "name": tool_name,
                    "parameters": params
                }
            )
            
            if "result" in response:
                return response["result"]
            else:
                # Handle error response
                if "error" in response:
                    error = response["error"]
                    code = error.get("code", 0)
                    
                    if code == 1100:  # INVALID_TOOL
                        raise InvalidToolError(tool_name, error.get("data"))
                    else:
                        raise ToolExecutionError(
                            tool_name,
                            error.get("message", "Unknown error"),
                            error.get("data")
                        )
                else:
                    raise ToolExecutionError(tool_name, "Invalid response from server")
                
        except TransportError as e:
            raise ToolExecutionError(
                tool_name, 
                f"Transport error: {e.message}", 
                {"cause": str(e.cause) if e.cause else None}
            )
    
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
        try:
            response_stream = self.transport.send_streaming_message(
                MessageMethod.TOOLS_CALL,
                {
                    "name": tool_name,
                    "parameters": params
                }
            )
            
            async for response in response_stream:
                if "result" in response:
                    yield response["result"]
                elif "error" in response:
                    # Handle error response
                    error = response["error"]
                    code = error.get("code", 0)
                    
                    if code == 1100:  # INVALID_TOOL
                        raise InvalidToolError(tool_name, error.get("data"))
                    else:
                        raise ToolExecutionError(
                            tool_name,
                            error.get("message", "Unknown error"),
                            error.get("data")
                        )
                
        except TransportError as e:
            raise ToolExecutionError(
                tool_name, 
                f"Transport error: {e.message}", 
                {"cause": str(e.cause) if e.cause else None}
            )
    
    async def get_prompts(self) -> List[Dict[str, Any]]:
        """
        Get available prompts from the server.
        
        Returns:
            List of prompt definitions
            
        Raises:
            ProtocolError: If an error occurs
        """
        try:
            response = await self.transport.send_message(MessageMethod.PROMPTS_LIST, {})
            
            if "result" in response:
                return response["result"].get("prompts", [])
            else:
                # Handle error response
                if "error" in response:
                    error = response["error"]
                    raise MCPProtocolError(
                        error.get("message", "Unknown error"),
                        error.get("code", 0),
                        error.get("data")
                    )
                else:
                    return []
                
        except TransportError as e:
            raise MCPProtocolError(f"Transport error: {e.message}", 0, {"cause": str(e.cause) if e.cause else None})
    
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
        try:
            request_params = {"name": prompt_name}
            if params:
                request_params["parameters"] = params
                
            response = await self.transport.send_message(MessageMethod.PROMPTS_GET, request_params)
            
            if "result" in response:
                return response["result"]
            else:
                # Handle error response
                if "error" in response:
                    error = response["error"]
                    raise MCPProtocolError(
                        error.get("message", "Unknown error"),
                        error.get("code", 0),
                        error.get("data")
                    )
                else:
                    raise MCPProtocolError("Invalid response from server", 0)
                
        except TransportError as e:
            raise MCPProtocolError(f"Transport error: {e.message}", 0, {"cause": str(e.cause) if e.cause else None})
    
    async def get_resources(self) -> List[Dict[str, Any]]:
        """
        Get available resources from the server.
        
        Returns:
            List of resource definitions
            
        Raises:
            ProtocolError: If an error occurs
        """
        try:
            response = await self.transport.send_message(MessageMethod.RESOURCES_LIST, {})
            
            if "result" in response:
                return response["result"].get("resources", [])
            else:
                # Handle error response
                if "error" in response:
                    error = response["error"]
                    raise MCPProtocolError(
                        error.get("message", "Unknown error"),
                        error.get("code", 0),
                        error.get("data")
                    )
                else:
                    return []
                
        except TransportError as e:
            raise MCPProtocolError(f"Transport error: {e.message}", 0, {"cause": str(e.cause) if e.cause else None})
    
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
        try:
            request_params = {"name": resource_name}
            if params:
                request_params["parameters"] = params
                
            response = await self.transport.send_message(MessageMethod.RESOURCES_GET, request_params)
            
            if "result" in response:
                return response["result"]
            else:
                # Handle error response
                if "error" in response:
                    error = response["error"]
                    raise MCPProtocolError(
                        error.get("message", "Unknown error"),
                        error.get("code", 0),
                        error.get("data")
                    )
                else:
                    raise MCPProtocolError("Invalid response from server", 0)
                
        except TransportError as e:
            raise MCPProtocolError(f"Transport error: {e.message}", 0, {"cause": str(e.cause) if e.cause else None})
    
    async def shutdown(self) -> bool:
        """
        Shutdown the connection.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        try:
            await self.transport.send_message(MessageMethod.SHUTDOWN, {})
            await self.transport.disconnect()
            return True
        except Exception as e:
            self.logger.warning(f"Shutdown error: {str(e)}")
            return False
