# src/mcp/transport/stdio/stdio_transport.py
"""
STDIO transport implementation for MCP protocol.

This module provides a transport implementation that communicates
with an MCP server via standard input/output.
"""
import json
import asyncio
import sys
import logging
import subprocess
from typing import Any, Dict, Optional, AsyncGenerator, Union

from mcp.transport.base.transport import Transport, TransportError
from mcp.messages.json_rpc_message import create_request


class StdioTransport(Transport):
    """Transport implementation using stdio."""
    
    def __init__(self, process: Optional[subprocess.Popen] = None):
        """
        Initialize the STDIO transport.
        
        Args:
            process: The subprocess to communicate with (optional)
                    If not provided, the transport will use sys.stdin/stdout
        """
        self.process = process
        self.reader = None
        self.writer = None
        self.request_id = 0
        self.logger = logging.getLogger("mcp-cli.stdio-transport")
    
    async def connect(self) -> bool:
        """
        Connect to the server.
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            if self.process:
                # Create StreamReader for the process stdout
                self.reader = asyncio.StreamReader()
                protocol = asyncio.StreamReaderProtocol(self.reader)
                
                # Connect to process stdout for reading
                transport, _ = await asyncio.get_event_loop().connect_read_pipe(
                    lambda: protocol, 
                    self.process.stdout
                )
                
                # Connect to process stdin for writing
                self.writer, _ = await asyncio.get_event_loop().connect_write_pipe(
                    lambda: asyncio.BaseProtocol(), 
                    self.process.stdin
                )
            else:
                # Use sys.stdin and sys.stdout
                self.reader = asyncio.StreamReader()
                protocol = asyncio.StreamReaderProtocol(self.reader)
                
                # Connect to stdin/stdout
                transport, _ = await asyncio.get_event_loop().connect_read_pipe(
                    lambda: protocol, 
                    sys.stdin
                )
                
                self.writer, _ = await asyncio.get_event_loop().connect_write_pipe(
                    lambda: asyncio.BaseProtocol(), 
                    sys.stdout
                )
            
            self.logger.debug("Connected to server via stdio")
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to server: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from the server.
        
        Returns:
            True if disconnected successfully, False otherwise
        """
        try:
            if self.writer:
                self.writer.close()
                self.reader = None
                self.writer = None
                
                # If using process, wait for it to end
                if self.process and self.process.poll() is None:
                    try:
                        self.process.terminate()
                        await asyncio.sleep(0.1)
                        if self.process.poll() is None:
                            self.process.kill()
                    except Exception as e:
                        self.logger.warning(f"Error terminating process: {str(e)}")
            
            self.logger.debug("Disconnected from server")
            return True
            
        except Exception as e:
            self.logger.error(f"Error disconnecting from server: {str(e)}")
            return False
    
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
        if not self.writer or not self.reader:
            raise TransportError("Not connected to server")
        
        # Get a unique request ID
        self.request_id += 1
        request_id = self.request_id
        
        try:
            # Create the request
            request = create_request(method, params, request_id)
            
            # Convert to JSON and add newline
            request_json = json.dumps(request) + "\n"
            
            # Log the request
            self.logger.debug(f"Sending request: {request_json.strip()}")
            
            # Send the request
            self.writer.write(request_json.encode())
            await self.writer.drain()
            
            # Read the response
            response_line = await self.reader.readline()
            if not response_line:
                raise TransportError("Connection closed by server")
            
            # Parse the response
            try:
                response_str = response_line.decode().strip()
                self.logger.debug(f"Received response: {response_str}")
                response = json.loads(response_str)
            except json.JSONDecodeError as e:
                raise TransportError(f"Invalid JSON in response: {response_line.decode()}", e)
            
            # Verify it's for our request
            if "id" not in response or response["id"] != request_id:
                raise TransportError(
                    f"Response ID mismatch: expected {request_id}, got {response.get('id')}"
                )
            
            return response
            
        except asyncio.CancelledError:
            # Re-raise cancellation
            raise
        except Exception as e:
            if isinstance(e, TransportError):
                raise
            else:
                raise TransportError(f"Error sending message: {str(e)}", e)
    
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
        if not self.writer or not self.reader:
            raise TransportError("Not connected to server")
        
        # Get a unique request ID
        self.request_id += 1
        request_id = self.request_id
        
        try:
            # Create the request
            request = create_request(method, params, request_id)
            
            # Convert to JSON and add newline
            request_json = json.dumps(request) + "\n"
            
            # Log the request
            self.logger.debug(f"Sending streaming request: {request_json.strip()}")
            
            # Send the request
            self.writer.write(request_json.encode())
            await self.writer.drain()
            
            # Read responses until complete
            while True:
                response_line = await self.reader.readline()
                if not response_line:
                    # Connection closed
                    self.logger.debug("Connection closed by server in streaming response")
                    break
                
                # Parse the response
                try:
                    response_str = response_line.decode().strip()
                    self.logger.debug(f"Received streaming response chunk: {response_str}")
                    response = json.loads(response_str)
                except json.JSONDecodeError as e:
                    raise TransportError(f"Invalid JSON in streaming response: {response_line.decode()}", e)
                
                # Verify it's for our request
                if "id" not in response or response["id"] != request_id:
                    # Skip responses that don't match our request ID
                    self.logger.warning(f"Skipping response with mismatched ID: {response.get('id')}")
                    continue
                
                # Yield the response
                yield response
                
                # If this is the final response (not partial), stop
                if "partial" not in response or not response["partial"]:
                    break
            
        except asyncio.CancelledError:
            # Re-raise cancellation
            raise
        except Exception as e:
            if isinstance(e, TransportError):
                raise
            else:
                raise TransportError(f"Error in streaming message: {str(e)}", e)
