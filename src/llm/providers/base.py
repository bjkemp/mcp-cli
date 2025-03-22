# src/llm/providers/base.py
"""
Base provider implementation.

This module provides a base class for LLM providers that implements
common functionality.
"""
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional
import logging

from llm.llm_client import LLMClient, LLMClientError


class BaseProvider(LLMClient, ABC):
    """Base class for LLM providers."""
    
    # Provider type identifier - should be overridden by subclasses
    PROVIDER_TYPE = "base"
    
    def __init__(self, model_name: Optional[str] = None, base_url: Optional[str] = None, 
                 streaming: bool = True, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the base provider.
        
        Args:
            model_name: Name of the model to use
            base_url: Base URL for the API
            streaming: Whether to support streaming responses
            api_key: API key for authentication
            **kwargs: Additional provider-specific options
        """
        self.model_name = model_name
        self.base_url = base_url
        self.streaming = streaming
        self.api_key = api_key
        self.available_tools = []
        self.system_prompt_generator = None
        self.options = kwargs
        self.logger = logging.getLogger(f"mcp-cli.provider.{self.PROVIDER_TYPE}")
    
    def set_tools(self, tools: List[Dict[str, Any]]) -> None:
        """
        Set available tools.
        
        Args:
            tools: List of tool definitions
        """
        self.available_tools = tools
        self.logger.debug(f"Set {len(tools)} tools for {self.PROVIDER_TYPE} provider")
    
    def set_system_prompt_generator(self, generator: Callable[[Dict[str, Any]], str]) -> None:
        """
        Set the system prompt generator.
        
        Args:
            generator: Function that generates system prompts
        """
        self.system_prompt_generator = generator
        self.logger.debug(f"Set system prompt generator for {self.PROVIDER_TYPE} provider")
    
    def generate_system_prompt(self, capabilities: Dict[str, Any]) -> str:
        """
        Generate a system prompt based on capabilities.
        
        Args:
            capabilities: Server capabilities
            
        Returns:
            The generated system prompt
        """
        if self.system_prompt_generator:
            return self.system_prompt_generator(capabilities)
        
        # Default system prompt
        tools_str = "\n".join([f"- {tool['name']}: {tool['description']}" 
                              for tool in self.available_tools
                              if 'name' in tool and 'description' in tool])
        
        prompt = (
            "You are a helpful assistant with access to tools.\n\n"
        )
        
        if tools_str:
            prompt += f"Available tools:\n{tools_str}\n\n"
            prompt += "When you need to use a tool, indicate the tool name and parameters clearly.\n"
        
        return prompt
    
    def change_model(self, model_name: str) -> bool:
        """
        Change the model being used.
        
        Args:
            model_name: Name of the model to use
            
        Returns:
            True if the model was changed successfully, False otherwise
        """
        self.model_name = model_name
        self.logger.info(f"Changed model to {model_name} for {self.PROVIDER_TYPE} provider")
        return True
