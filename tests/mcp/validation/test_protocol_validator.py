# tests/mcp/validation/test_protocol_validator.py
"""
Tests for the MCP protocol validator.
"""
import pytest
from src.mcp.validation.protocol_validator import ProtocolValidator


def test_validate_valid_request():
    """Test validating a valid JSON-RPC request."""
    valid_request = {
        "jsonrpc": "2.0",
        "method": "ping",
        "params": {},
        "id": 1
    }
    
    error = ProtocolValidator.validate_request(valid_request)
    assert error is None


def test_validate_invalid_requests():
    """Test validating invalid JSON-RPC requests."""
    # Test cases with expected error messages
    test_cases = [
        (
            {"method": "ping", "params": {}, "id": 1},
            "Missing required field: 'jsonrpc'"
        ),
        (
            {"jsonrpc": "1.0", "method": "ping", "params": {}, "id": 1},
            "Invalid 'jsonrpc' value: must be '2.0'"
        ),
        (
            {"jsonrpc": "2.0", "params": {}, "id": 1},
            "Missing required field: 'method'"
        ),
        (
            {"jsonrpc": "2.0", "method": 123, "params": {}, "id": 1},
            "Invalid 'method' type: must be a string"
        ),
        (
            {"jsonrpc": "2.0", "method": "ping", "id": 1},
            "Missing required field: 'params'"
        ),
        (
            {"jsonrpc": "2.0", "method": "ping", "params": "invalid", "id": 1},
            "Invalid 'params' type: must be an object"
        ),
        (
            {"jsonrpc": "2.0", "method": "ping", "params": {}},
            "Missing required field: 'id'"
        ),
        (
            {"jsonrpc": "2.0", "method": "ping", "params": {}, "id": True},
            "Invalid 'id' type: must be a string or number"
        )
    ]
    
    for invalid_request, expected_error in test_cases:
        error = ProtocolValidator.validate_request(invalid_request)
        assert error is not None
        assert error == expected_error


def test_validate_valid_response():
    """Test validating a valid JSON-RPC response."""
    # Success response
    valid_success = {
        "jsonrpc": "2.0",
        "result": {"status": "success"},
        "id": 1
    }
    
    error = ProtocolValidator.validate_response(valid_success)
    assert error is None
    
    # Error response
    valid_error = {
        "jsonrpc": "2.0",
        "error": {
            "code": 404,
            "message": "Not found"
        },
        "id": 1
    }
    
    error = ProtocolValidator.validate_response(valid_error)
    assert error is None
    
    # Partial response
    valid_partial = {
        "jsonrpc": "2.0",
        "result": {"partial": "data"},
        "id": 1,
        "partial": True
    }
    
    error = ProtocolValidator.validate_response(valid_partial)
    assert error is None


def test_validate_invalid_responses():
    """Test validating invalid JSON-RPC responses."""
    # Test cases with expected error messages
    test_cases = [
        (
            {"result": {"status": "success"}, "id": 1},
            "Missing required field: 'jsonrpc'"
        ),
        (
            {"jsonrpc": "1.0", "result": {"status": "success"}, "id": 1},
            "Invalid 'jsonrpc' value: must be '2.0'"
        ),
        (
            {"jsonrpc": "2.0", "result": {"status": "success"}},
            "Missing required field: 'id'"
        ),
        (
            {"jsonrpc": "2.0", "id": 1},
            "Missing required field: either 'result' or 'error' must be present"
        ),
        (
            {"jsonrpc": "2.0", "result": {}, "error": {}, "id": 1},
            "Invalid response: cannot have both 'result' and 'error'"
        ),
        (
            {"jsonrpc": "2.0", "error": "invalid", "id": 1},
            "Invalid 'error' type: must be an object"
        ),
        (
            {"jsonrpc": "2.0", "error": {}, "id": 1},
            "Missing required field in error: 'code'"
        ),
        (
            {"jsonrpc": "2.0", "error": {"code": "404"}, "id": 1},
            "Invalid error 'code' type: must be a number"
        ),
        (
            {"jsonrpc": "2.0", "error": {"code": 404}, "id": 1},
            "Missing required field in error: 'message'"
        ),
        (
            {"jsonrpc": "2.0", "error": {"code": 404, "message": 123}, "id": 1},
            "Invalid error 'message' type: must be a string"
        ),
        (
            {"jsonrpc": "2.0", "result": {}, "id": 1, "partial": "invalid"},
            "Invalid 'partial' type: must be a boolean"
        )
    ]
    
    for invalid_response, expected_error in test_cases:
        error = ProtocolValidator.validate_response(invalid_response)
        assert error is not None
        assert error == expected_error


def test_validate_tool_results():
    """Test validating different tool results."""
    # Test readFile tool
    valid_read_file = {
        "content": "File content"
    }
    
    error = ProtocolValidator.validate_tool_result("readFile", valid_read_file)
    assert error is None
    
    invalid_read_file = {
        "wrong_field": "content"
    }
    
    error = ProtocolValidator.validate_tool_result("readFile", invalid_read_file)
    assert error is not None
    assert "missing required field 'content'" in error
    
    # Test writeFile tool
    valid_write_file = {
        "success": True,
        "message": "File written successfully"
    }
    
    error = ProtocolValidator.validate_tool_result("writeFile", valid_write_file)
    assert error is None
    
    invalid_write_file = {
        "success": "not_a_boolean"
    }
    
    error = ProtocolValidator.validate_tool_result("writeFile", invalid_write_file)
    assert error is not None
    assert "'success' must be a boolean" in error
    
    # Test listDirectory tool
    valid_list_dir = {
        "entries": [
            {"name": "file.txt", "type": "file"},
            {"name": "folder", "type": "directory"}
        ]
    }
    
    error = ProtocolValidator.validate_tool_result("listDirectory", valid_list_dir)
    assert error is None
    
    invalid_list_dir = {
        "entries": [
            {"name": "file.txt", "type": "unknown"}
        ]
    }
    
    error = ProtocolValidator.validate_tool_result("listDirectory", invalid_list_dir)
    assert error is not None
    assert "'type' must be 'file' or 'directory'" in error
    
    # Test query tool
    valid_query = {
        "rows": [
            {"id": 1, "name": "Test"}
        ]
    }
    
    error = ProtocolValidator.validate_tool_result("query", valid_query)
    assert error is None
    
    invalid_query = {
        "rows": "not_an_array"
    }
    
    error = ProtocolValidator.validate_tool_result("query", invalid_query)
    assert error is not None
    assert "'rows' must be an array" in error
