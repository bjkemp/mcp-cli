# src/llm/providers/mock_provider.py
"""
Mock provider implementation for testing.

This module provides a mock implementation of the LLM provider
interface for testing without real API calls.
"""
import json
import asyncio
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

from llm.providers.base import BaseProvider
from llm.llm_client import LLMClientError


class MockProvider(BaseProvider):
    """Mock LLM provider for testing."""
    
    PROVIDER_TYPE = "mock"
    
    def __init__(self, model_name: Optional[str] = "mock-model", **kwargs):
        """
        Initialize the mock provider.
        
        Args:
            model_name: Name of the model to use
            **kwargs: Additional provider-specific options
        """
        super().__init__(model_name=model_name, **kwargs)
        self.responses = {}
        self.streaming_responses = {}
        self.tool_calls = {}
    
    def add_response(self, messages_hash: str, response: str) -> None:
        """
        Add a predefined response for a message pattern.
        
        Args:
            messages_hash: Hash of the messages to match
            response: The response to return
        """
        self.responses[messages_hash] = response
    
    def add_streaming_response(self, messages_hash: str, chunks: List[str]) -> None:
        """
        Add a predefined streaming response.
        
        Args:
            messages_hash: Hash of the messages to match
            chunks: List of text chunks to return
        """
        self.streaming_responses[messages_hash] = chunks
    
    def add_tool_call(self, messages_hash: str, tool_name: str, params: Dict[str, Any]) -> None:
        """
        Add a predefined tool call.
        
        Args:
            messages_hash: Hash of the messages to match
            tool_name: Name of the tool to call
            params: Parameters for the tool
        """
        self.tool_calls[messages_hash] = {"tool_name": tool_name, "params": params}
    
    def _hash_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Create a simple hash for messages to use as lookup key.
        
        Args:
            messages: The messages to hash
            
        Returns:
            A string hash of the messages
        """
        # For testing, we can use the last user message as the hash
        for msg in reversed(messages):
            if msg["role"] == "user":
                return msg["content"]
        
        # If no user message is found, use an empty string
        return ""
    
    async def generate_text(self, messages: List[Dict[str, str]], 
                           tool_handler: Optional[Callable[[str, Dict[str, Any]], Any]] = None) -> str:
        """
        Generate text from a conversation.
        
        Args:
            messages: List of messages in the conversation
            tool_handler: Optional callback for handling tool calls
            
        Returns:
            The generated text
            
        Raises:
            LLMClientError: If an error occurs during text generation
        """
        # Get message hash
        messages_hash = self._hash_messages(messages)
        
        # Check if we should make a tool call
        if messages_hash in self.tool_calls and tool_handler:
            tool_call = self.tool_calls[messages_hash]
            try:
                await tool_handler(tool_call["tool_name"], tool_call["params"])
            except Exception as e:
                self.logger.warning(f"Tool call error: {str(e)}")
        
        # Return predefined response or default
        return self.responses.get(messages_hash, f"This is a mock response from {self.model_name}.")
    
    async def generate_streaming_text(self, messages: List[Dict[str, str]],
                                     tool_handler: Optional[Callable[[str, Dict[str, Any]], Any]] = None
                                     ) -> AsyncGenerator[str, None]:
        """
        Generate streaming text from a conversation.
        
        Args:
            messages: List of messages in the conversation
            tool_handler: Optional callback for handling tool calls
            
        Returns:
            An async generator yielding text chunks
            
        Raises:
            LLMClientError: If an error occurs during text generation
        """
        # Get message hash
        messages_hash = self._hash_messages(messages)
        
        # Check if we should make a tool call
        if messages_hash in self.tool_calls and tool_handler:
            tool_call = self.tool_calls[messages_hash]
            try:
                await tool_handler(tool_call["tool_name"], tool_call["params"])
            except Exception as e:
                self.logger.warning(f"Tool call error: {str(e)}")
        
        # Get predefined chunks or default
        chunks = self.streaming_responses.get(
            messages_hash, 
            [f"This ", f"is ", f"a ", f"mock ", f"streaming ", f"response ", f"from ", f"{self.model_name}."]
        )
        
        # Yield chunks with a small delay for realism
        for chunk in chunks:
            yield chunk
            await asyncio.sleep(0.05)
