# src/mcp/validation/protocol_validator.py
"""
Protocol Validator for MCP messages.

Validates that messages and responses conform to the MCP specification.
"""
import json
from typing import Any, Dict, Optional

# We'll use a simple validation approach first and can add jsonschema later if needed
class ProtocolValidator:
    """Validates MCP protocol messages and responses."""
    
    @classmethod
    def validate_request(cls, request: Dict[str, Any]) -> Optional[str]:
        """
        Validate a JSON-RPC request message.
        
        Args:
            request: The request to validate
            
        Returns:
            None if valid, error message otherwise
        """
        # Check required fields
        if "jsonrpc" not in request:
            return "Missing required field: 'jsonrpc'"
        if request["jsonrpc"] != "2.0":
            return "Invalid 'jsonrpc' value: must be '2.0'"
        
        if "method" not in request:
            return "Missing required field: 'method'"
        if not isinstance(request["method"], str):
            return "Invalid 'method' type: must be a string"
        
        if "params" not in request:
            return "Missing required field: 'params'"
        if not isinstance(request["params"], dict):
            return "Invalid 'params' type: must be an object"
        
        if "id" not in request:
            return "Missing required field: 'id'"
        if not isinstance(request["id"], (str, int)):
            return "Invalid 'id' type: must be a string or number"
        
        return None
    
    @classmethod
    def validate_response(cls, response: Dict[str, Any]) -> Optional[str]:
        """
        Validate a JSON-RPC response message.
        
        Args:
            response: The response to validate
            
        Returns:
            None if valid, error message otherwise
        """
        # Check required fields
        if "jsonrpc" not in response:
            return "Missing required field: 'jsonrpc'"
        if response["jsonrpc"] != "2.0":
            return "Invalid 'jsonrpc' value: must be '2.0'"
        
        if "id" not in response:
            return "Missing required field: 'id'"
        if not isinstance(response["id"], (str, int)) and response["id"] is not None:
            return "Invalid 'id' type: must be a string, number, or null"
        
        # Check result or error
        if "result" not in response and "error" not in response:
            return "Missing required field: either 'result' or 'error' must be present"
        
        if "error" in response and "result" in response:
            return "Invalid response: cannot have both 'result' and 'error'"
        
        # Validate error structure if present
        if "error" in response:
            error = response["error"]
            if not isinstance(error, dict):
                return "Invalid 'error' type: must be an object"
            
            if "code" not in error:
                return "Missing required field in error: 'code'"
            if not isinstance(error["code"], int):
                return "Invalid error 'code' type: must be a number"
            
            if "message" not in error:
                return "Missing required field in error: 'message'"
            if not isinstance(error["message"], str):
                return "Invalid error 'message' type: must be a string"
        
        # Check optional partial field
        if "partial" in response and not isinstance(response["partial"], bool):
            return "Invalid 'partial' type: must be a boolean"
        
        return None
    
    @classmethod
    def validate_tool_result(cls, tool_name: str, result: Dict[str, Any]) -> Optional[str]:
        """
        Validate a tool result against expected schema.
        
        Args:
            tool_name: Name of the tool
            result: The tool result to validate
            
        Returns:
            None if valid, error message otherwise
        """
        # Basic validation for common tools
        if tool_name == "readFile":
            if "content" not in result:
                return "Invalid result for readFile: missing required field 'content'"
        
        elif tool_name == "writeFile":
            if "success" not in result:
                return "Invalid result for writeFile: missing required field 'success'"
            if not isinstance(result["success"], bool):
                return "Invalid result for writeFile: 'success' must be a boolean"
        
        elif tool_name == "listDirectory":
            if "entries" not in result:
                return "Invalid result for listDirectory: missing required field 'entries'"
            if not isinstance(result["entries"], list):
                return "Invalid result for listDirectory: 'entries' must be an array"
            
            for entry in result["entries"]:
                if not isinstance(entry, dict):
                    return "Invalid result for listDirectory: each entry must be an object"
                if "name" not in entry:
                    return "Invalid result for listDirectory: each entry must have a 'name'"
                if "type" not in entry:
                    return "Invalid result for listDirectory: each entry must have a 'type'"
                if entry["type"] not in ["file", "directory"]:
                    return "Invalid result for listDirectory: 'type' must be 'file' or 'directory'"
        
        elif tool_name == "query":
            if "rows" not in result:
                return "Invalid result for query: missing required field 'rows'"
            if not isinstance(result["rows"], list):
                return "Invalid result for query: 'rows' must be an array"
        
        elif tool_name == "getTables":
            if "tables" not in result:
                return "Invalid result for getTables: missing required field 'tables'"
        
        # For unrecognized tools, we perform minimal validation
        return None
