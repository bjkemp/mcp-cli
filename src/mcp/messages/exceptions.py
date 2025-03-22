# src/mcp/messages/exceptions.py
"""
MCP protocol exceptions.

This module defines the exceptions used for MCP protocol errors.
"""
from typing import Any, Dict, Optional

from src.mcp.messages.error_codes import ErrorCodes


class MCPProtocolError(Exception):
    """Base class for MCP protocol errors."""
    
    def __init__(self, message: str, code: int, data: Optional[Dict[str, Any]] = None):
        """
        Initialize a new MCP protocol error.
        
        Args:
            message: Error message
            code: Error code
            data: Additional error data
        """
        self.message = message
        self.code = code
        self.data = data
        super().__init__(message)
    
    def to_json_rpc_error(self) -> Dict[str, Any]:
        """
        Convert to a JSON-RPC error object.
        
        Returns:
            A JSON-RPC error object
        """
        error = {
            "code": self.code,
            "message": self.message
        }
        
        if self.data:
            error["data"] = self.data
            
        return error


class ParseError(MCPProtocolError):
    """Error raised when request parsing fails."""
    
    def __init__(self, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        message = message or ErrorCodes.get_message(ErrorCodes.PARSE_ERROR)
        super().__init__(message, ErrorCodes.PARSE_ERROR, data)


class InvalidRequestError(MCPProtocolError):
    """Error raised when a request is invalid."""
    
    def __init__(self, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        message = message or ErrorCodes.get_message(ErrorCodes.INVALID_REQUEST)
        super().__init__(message, ErrorCodes.INVALID_REQUEST, data)


class MethodNotFoundError(MCPProtocolError):
    """Error raised when a requested method is not found."""
    
    def __init__(self, method: str, data: Optional[Dict[str, Any]] = None):
        message = f"Method not found: {method}"
        super().__init__(message, ErrorCodes.METHOD_NOT_FOUND, data)


class InvalidParamsError(MCPProtocolError):
    """Error raised when request parameters are invalid."""
    
    def __init__(self, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        message = message or ErrorCodes.get_message(ErrorCodes.INVALID_PARAMS)
        super().__init__(message, ErrorCodes.INVALID_PARAMS, data)


class InternalError(MCPProtocolError):
    """Error raised when an internal error occurs."""
    
    def __init__(self, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        message = message or ErrorCodes.get_message(ErrorCodes.INTERNAL_ERROR)
        super().__init__(message, ErrorCodes.INTERNAL_ERROR, data)


class InitializationError(MCPProtocolError):
    """Error raised when initialization fails."""
    
    def __init__(self, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        message = message or ErrorCodes.get_message(ErrorCodes.INITIALIZATION_FAILED)
        super().__init__(message, ErrorCodes.INITIALIZATION_FAILED, data)


class InvalidToolError(MCPProtocolError):
    """Error raised when a requested tool is invalid."""
    
    def __init__(self, tool: str, data: Optional[Dict[str, Any]] = None):
        message = f"Invalid tool: {tool}"
        super().__init__(message, ErrorCodes.INVALID_TOOL, data)


class ToolExecutionError(MCPProtocolError):
    """Error raised when tool execution fails."""
    
    def __init__(self, tool: str, message: str, data: Optional[Dict[str, Any]] = None):
        full_message = f"Tool execution failed ({tool}): {message}"
        super().__init__(full_message, ErrorCodes.TOOL_EXECUTION_FAILED, data)


class FileNotFoundError(MCPProtocolError):
    """Error raised when a file is not found."""
    
    def __init__(self, path: str, data: Optional[Dict[str, Any]] = None):
        message = f"File not found: {path}"
        super().__init__(message, ErrorCodes.FS_FILE_NOT_FOUND, data)


class PermissionDeniedError(MCPProtocolError):
    """Error raised when permission is denied."""
    
    def __init__(self, path: str, data: Optional[Dict[str, Any]] = None):
        message = f"Permission denied: {path}"
        super().__init__(message, ErrorCodes.FS_PERMISSION_DENIED, data)


class IOError(MCPProtocolError):
    """Error raised when an I/O error occurs."""
    
    def __init__(self, path: str, message: str, data: Optional[Dict[str, Any]] = None):
        full_message = f"I/O error ({path}): {message}"
        super().__init__(full_message, ErrorCodes.FS_IO_ERROR, data)


class InvalidPathError(MCPProtocolError):
    """Error raised when a path is invalid."""
    
    def __init__(self, path: str, data: Optional[Dict[str, Any]] = None):
        message = f"Invalid path: {path}"
        super().__init__(message, ErrorCodes.FS_INVALID_PATH, data)


class DatabaseError(MCPProtocolError):
    """Error raised when a database error occurs."""
    
    def __init__(self, message: str, code: int = ErrorCodes.DB_QUERY_ERROR, data: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, data)


class TableNotFoundError(DatabaseError):
    """Error raised when a table is not found."""
    
    def __init__(self, table: str, data: Optional[Dict[str, Any]] = None):
        message = f"Table not found: {table}"
        super().__init__(message, ErrorCodes.DB_TABLE_NOT_FOUND, data)
