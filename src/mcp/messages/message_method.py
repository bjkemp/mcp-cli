# src/mcp/messages/message_method.py
"""
MCP protocol message methods.

This module defines the standard method names used in the MCP protocol.
"""


class MessageMethod:
    """Constants for MCP protocol message methods."""
    
    # Core methods
    INITIALIZE = "initialize"
    SHUTDOWN = "shutdown"
    PING = "ping"
    
    # Tool methods
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    
    # Prompt methods
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"
    
    # Resource methods
    RESOURCES_LIST = "resources/list"
    RESOURCES_GET = "resources/get"
    
    # Filesystem methods (for direct tool calling)
    FS_READ_FILE = "fs/readFile"
    FS_WRITE_FILE = "fs/writeFile"
    FS_LIST_DIRECTORY = "fs/listDirectory"
    
    # SQLite methods (for direct tool calling)
    DB_QUERY = "db/query"
    DB_GET_TABLES = "db/getTables"
    
    @classmethod
    def is_valid_method(cls, method: str) -> bool:
        """
        Check if a method name is valid.
        
        Args:
            method: The method name to check
            
        Returns:
            True if the method is valid, False otherwise
        """
        return method in [
            cls.INITIALIZE,
            cls.SHUTDOWN,
            cls.PING,
            cls.TOOLS_LIST,
            cls.TOOLS_CALL,
            cls.PROMPTS_LIST,
            cls.PROMPTS_GET,
            cls.RESOURCES_LIST,
            cls.RESOURCES_GET,
            cls.FS_READ_FILE,
            cls.FS_WRITE_FILE,
            cls.FS_LIST_DIRECTORY,
            cls.DB_QUERY,
            cls.DB_GET_TABLES
        ]
