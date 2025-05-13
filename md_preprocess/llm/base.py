"""
Base LLM adapter class for MD Preprocess library.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseLLMAdapter(ABC):
    """
    Abstract base class for LLM adapters.
    """
    
    @abstractmethod
    def send_prompt(self, prompt: str, file_content: str) -> str:
        """
        Send prompt to LLM and receive response.
        
        Args:
            prompt: The prompt to send to the LLM
            file_content: Content of the file being processed (for context)
            
        Returns:
            Response from the LLM
        """
        pass
    
    @abstractmethod
    def format_error_for_retry(
        self, 
        original_prompt: str, 
        error_info: Dict[str, Any], 
        code: str
    ) -> str:
        """
        Format error information for retry prompt.
        
        Args:
            original_prompt: The original prompt sent to the LLM
            error_info: Information about the error that occurred
            code: The code that produced the error
            
        Returns:
            Formatted retry prompt
        """
        pass