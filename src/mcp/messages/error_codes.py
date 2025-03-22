# src/mcp/messages/error_codes.py
"""
MCP protocol error codes.

This module defines the standard error codes used in the MCP protocol.
"""


class ErrorCodes:
    """Constants for MCP protocol error codes."""
    
    # JSON-RPC standard error codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # MCP specific error codes
    INITIALIZATION_FAILED = 1000
    INVALID_TOOL = 1100
    TOOL_EXECUTION_FAILED = 1101
    INVALID_PROMPT = 1200
    PROMPT_NOT_FOUND = 1201
    INVALID_RESOURCE = 1300
    RESOURCE_NOT_FOUND = 1301
    
    # File system error codes
    FS_FILE_NOT_FOUND = 2000
    FS_PERMISSION_DENIED = 2001
    FS_IO_ERROR = 2002
    FS_INVALID_PATH = 2003
    
    # Database error codes
    DB_CONNECTION_ERROR = 3000
    DB_QUERY_ERROR = 3001
    DB_TABLE_NOT_FOUND = 3002
    
    @classmethod
    def get_message(cls, code: int) -> str:
        """
        Get the default message for an error code.
        
        Args:
            code: The error code
            
        Returns:
            The default error message
        """
        messages = {
            cls.PARSE_ERROR: "Parse error",
            cls.INVALID_REQUEST: "Invalid request",
            cls.METHOD_NOT_FOUND: "Method not found",
            cls.INVALID_PARAMS: "Invalid parameters",
            cls.INTERNAL_ERROR: "Internal error",
            cls.INITIALIZATION_FAILED: "Initialization failed",
            cls.INVALID_TOOL: "Invalid tool",
            cls.TOOL_EXECUTION_FAILED: "Tool execution failed",
            cls.INVALID_PROMPT: "Invalid prompt",
            cls.PROMPT_NOT_FOUND: "Prompt not found",
            cls.INVALID_RESOURCE: "Invalid resource",
            cls.RESOURCE_NOT_FOUND: "Resource not found",
            cls.FS_FILE_NOT_FOUND: "File not found",
            cls.FS_PERMISSION_DENIED: "Permission denied",
            cls.FS_IO_ERROR: "I/O error",
            cls.FS_INVALID_PATH: "Invalid path",
            cls.DB_CONNECTION_ERROR: "Database connection error",
            cls.DB_QUERY_ERROR: "Database query error",
            cls.DB_TABLE_NOT_FOUND: "Table not found"
        }
        
        return messages.get(code, "Unknown error")
