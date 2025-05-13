"""
Claude LLM adapter for MD Preprocess library.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, Optional

try:
    import anthropic
except ImportError:
    anthropic = None

from md_preprocess.llm.base import BaseLLMAdapter
from md_preprocess.utils.logging_utils import log_progress


class ClaudeAdapter(BaseLLMAdapter):
    """
    Adapter for Anthropic's Claude API.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model: str = "claude-3-7-sonnet-20250219",
        max_tokens: int = 4000,
        temperature: float = 0.2,
        use_cache: bool = True,
        cache_dir: str = ".cache/claude_responses"
    ):
        """
        Initialize the Claude adapter.
        
        Args:
            api_key: API key for Anthropic's Claude API
            model: Model to use (default: claude-3-7-sonnet-20250219)
            max_tokens: Maximum tokens in the response
            temperature: Temperature parameter for generation
            use_cache: Whether to cache responses
            cache_dir: Directory for response cache
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        if not anthropic:
            raise ImportError(
                "The 'anthropic' package is required. "
                "Install it with 'pip install anthropic'"
            )
            
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.use_cache = use_cache
        self.cache_dir = cache_dir
        
        if self.use_cache and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.logger = logging.getLogger("md_preprocess.claude_adapter")
    
    def send_prompt(self, prompt: str, file_content: str) -> str:
        """
        Send prompt to Claude and receive response.
        
        Args:
            prompt: The prompt to send to Claude
            file_content: Content of the file being processed
            
        Returns:
            Response from Claude
        """
        # Create a full system prompt that includes the file content
        system_prompt = prompt
        if file_content:
            # Truncate file content if too large (to avoid token limits)
            if len(file_content) > 300000:  # Arbitrary limit to avoid token issues
                file_content = file_content[:150000] + "\n\n[...content truncated...]\n\n" + file_content[-150000:]
            
            system_prompt += f"\n\nHere is the content of the input file:\n\n{file_content}"
        
        # Check cache first if enabled
        if self.use_cache:
            cache_key = self._get_cache_key(system_prompt)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                log_progress("Using cached LLM response")
                return cached_response
        
        # Make API request
        log_progress(f"Sending request to Claude ({self.model})...")
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": "Generate Python code to preprocess this markdown file as described."}
                ]
            )
            
            content = response.content[0].text
            
            # Cache the response if enabled
            if self.use_cache:
                self._cache_response(cache_key, content)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Claude API request failed: {str(e)}")
            raise
    
    def format_error_for_retry(
        self, 
        original_prompt: str, 
        error_info: Dict[str, Any], 
        code: str
    ) -> str:
        """
        Format error information for retry prompt to Claude.
        
        Args:
            original_prompt: The original prompt sent to Claude
            error_info: Information about the error that occurred
            code: The code that produced the error
            
        Returns:
            Formatted retry prompt
        """
        return (
            f"{original_prompt}\n\n"
            f"The Python code you provided encountered an error:\n\n"
            f"Error: {error_info.get('error_message', 'Unknown error')}\n"
            f"At line {error_info.get('line_number', 'Unknown')}: {error_info.get('error_line', '')}\n\n"
            f"Full code:\n```python\n{code}\n```\n\n"
            f"Please fix the error and provide corrected code that performs the same preprocessing task."
        )
    
    def _get_cache_key(self, prompt: str) -> str:
        """
        Generate a cache key for a prompt.
        
        Args:
            prompt: The prompt to generate a key for
            
        Returns:
            Cache key string
        """
        # Create hash of the prompt for the cache key
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        return f"{self.model}_{prompt_hash}"
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """
        Retrieve a cached response if available.
        
        Args:
            cache_key: Cache key to look up
            
        Returns:
            Cached response or None if not found
        """
        if not self.use_cache:
            return None
            
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get("response")
            except Exception as e:
                self.logger.warning(f"Failed to read cache: {str(e)}")
                
        return None
    
    def _cache_response(self, cache_key: str, response: str) -> None:
        """
        Cache a response for future use.
        
        Args:
            cache_key: Cache key to store under
            response: Response to cache
        """
        if not self.use_cache:
            return
            
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "response": response,
                    "model": self.model,
                    "timestamp": os.path.getmtime(cache_file) if os.path.exists(cache_file) else None
                }, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to write cache: {str(e)}")