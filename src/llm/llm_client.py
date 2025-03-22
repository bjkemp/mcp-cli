# src/llm/llm_client.py
"""
LLM client interface.

This module defines the abstract LLMClient interface that all
LLM client implementations must follow.
"""
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union


class LLMClient(ABC):
    """Interface for LLM clients."""
    
    @abstractmethod
    async def generate_text(self, messages: List[Dict[str, str]], 
                           tool_handler: Optional[Callable[[str, Dict[str, Any]], Any]] = None) -> str:
        """
        Generate text from a conversation.
        
        Args:
            messages: List of messages in the conversation
            tool_handler: Optional callback for handling tool calls
                         Should take a tool name and parameters and return a result
            
        Returns:
            The generated text
            
        Raises:
            LLMClientError: If an error occurs during text generation
        """
        pass
    
    @abstractmethod
    async def generate_streaming_text(self, messages: List[Dict[str, str]],
                                     tool_handler: Optional[Callable[[str, Dict[str, Any]], Any]] = None
                                     ) -> AsyncGenerator[str, None]:
        """
        Generate streaming text from a conversation.
        
        Args:
            messages: List of messages in the conversation
            tool_handler: Optional callback for handling tool calls
                         Should take a tool name and parameters and return a result
            
        Returns:
            An async generator yielding text chunks
            
        Raises:
            LLMClientError: If an error occurs during text generation
        """
        pass
    
    @abstractmethod
    def set_tools(self, tools: List[Dict[str, Any]]) -> None:
        """
        Set available tools.
        
        Args:
            tools: List of tool definitions
        """
        pass
    
    @abstractmethod
    def generate_system_prompt(self, capabilities: Dict[str, Any]) -> str:
        """
        Generate a system prompt based on capabilities.
        
        Args:
            capabilities: Server capabilities
            
        Returns:
            The generated system prompt
        """
        pass
    
    @abstractmethod
    def change_model(self, model_name: str) -> bool:
        """
        Change the model being used.
        
        Args:
            model_name: Name of the model to use
            
        Returns:
            True if the model was changed successfully, False otherwise
        """
        pass


class LLMClientError(Exception):
    """Error raised when an LLM client error occurs."""
    
    def __init__(self, message: str, provider: str, model: Optional[str] = None, 
                 cause: Optional[Exception] = None):
        """
        Initialize a new LLM client error.
        
        Args:
            message: Error message
            provider: Provider name
            model: Model name (optional)
            cause: The underlying cause (optional)
        """
        self.message = message
        self.provider = provider
        self.model = model
        self.cause = cause
        
        full_message = f"LLM error ({provider}"
        if model:
            full_message += f", {model}"
        full_message += f"): {message}"
        
        super().__init__(full_message)
