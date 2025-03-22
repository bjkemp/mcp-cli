# src/mcp/messages/json_rpc_message.py
"""
JSON-RPC message utilities for MCP protocol.

This module provides functions for creating and validating JSON-RPC messages
used in the MCP protocol.
"""
from typing import Any, Dict, Optional, Union, List

from mcp.validation.protocol_validator import ProtocolValidator


def create_request(method: str, params: Dict[str, Any], request_id: Union[str, int]) -> Dict[str, Any]:
    """
    Create a JSON-RPC request message.
    
    Args:
        method: The method name to call
        params: Parameters for the method
        request_id: Unique identifier for the request
        
    Returns:
        A JSON-RPC request object
    """
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id
    }
    
    # Validate the request
    error = ProtocolValidator.validate_request(request)
    if error:
        raise ValueError(f"Invalid request: {error}")
    
    return request


def create_response(result: Any, request_id: Union[str, int], partial: bool = False) -> Dict[str, Any]:
    """
    Create a JSON-RPC response message.
    
    Args:
        result: The result data
        request_id: Identifier matching the request
        partial: Whether this is a partial response
        
    Returns:
        A JSON-RPC response object
    """
    response = {
        "jsonrpc": "2.0",
        "result": result,
        "id": request_id
    }
    
    if partial:
        response["partial"] = True
    
    # Validate the response
    error = ProtocolValidator.validate_response(response)
    if error:
        raise ValueError(f"Invalid response: {error}")
    
    return response


def create_error(code: int, message: str, request_id: Union[str, int], data: Optional[Any] = None) -> Dict[str, Any]:
    """
    Create a JSON-RPC error response message.
    
    Args:
        code: Error code
        message: Error message
        request_id: Identifier matching the request
        data: Additional error data (optional)
        
    Returns:
        A JSON-RPC error response object
    """
    error_response = {
        "jsonrpc": "2.0",
        "error": {
            "code": code,
            "message": message
        },
        "id": request_id
    }
    
    if data is not None:
        error_response["error"]["data"] = data
    
    # Validate the response
    error = ProtocolValidator.validate_response(error_response)
    if error:
        raise ValueError(f"Invalid error response: {error}")
    
    return error_response


def validate_message(message: Dict[str, Any]) -> Optional[str]:
    """
    Validate a JSON-RPC message.
    
    Args:
        message: The message to validate
        
    Returns:
        None if valid, error message otherwise
    """
    # Determine if this is a request or response
    if "method" in message:
        return ProtocolValidator.validate_request(message)
    else:
        return ProtocolValidator.validate_response(message)
