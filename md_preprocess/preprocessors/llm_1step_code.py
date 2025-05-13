"""
LLM1StepCode preprocessor for MD Preprocess library.

This preprocessor uses an LLM to generate Python code that performs the preprocessing,
then executes that code to process the markdown file.
"""

import os
import logging
from typing import Optional, Dict, Any, List

from md_preprocess.preprocessors.base import BasePreprocessor
from md_preprocess.llm.base import BaseLLMAdapter
from md_preprocess.utils.code_executor import execute_python_code, format_error_details
from md_preprocess.utils.logging_utils import log_progress
from md_preprocess.config import CORRECTION_PROMPT, ERROR_RETRY_PROMPT


class LLM1StepCode(BasePreprocessor):
    """
    Preprocessor that uses LLMs to generate Python code for cleaning and structuring MD files.
    """
    
    def __init__(self, llm_adapter: BaseLLMAdapter, max_attempts: int = 3):
        """
        Initialize the LLM1StepCode preprocessor.
        
        Args:
            llm_adapter: Adapter for communicating with the LLM
            max_attempts: Maximum number of retry attempts for code execution
        """
        super().__init__()
        self.llm_adapter = llm_adapter
        self.max_attempts = max_attempts
        self.logger = logging.getLogger("md_preprocess.llm_1step_code")
    
    def preprocess(self, input_file: str, output_file: str) -> bool:
        """
        Preprocess the input file using LLM-generated Python code.
        
        Args:
            input_file: Path to the input markdown file
            output_file: Path where the output should be written
            
        Returns:
            Boolean indicating success or failure
        """
        # Read input file
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except Exception as e:
            self.add_error(f"Failed to read input file: {str(e)}")
            log_progress(f"Failed to read input file: {str(e)}", level="error")
            return False
        
        # Prepare prompt with actual file paths
        prompt = CORRECTION_PROMPT.format(
            input_file=input_file,
            output_file=output_file
        )
        
        # Send to LLM
        log_progress("Sending prompt to LLM for code generation")
        try:
            response = self.llm_adapter.send_prompt(prompt, file_content)
        except Exception as e:
            self.add_error(f"LLM request failed: {str(e)}")
            log_progress(f"LLM request failed: {str(e)}", level="error")
            return False
        
        # Extract Python code from response
        code = self._extract_code(response)
        if not code:
            self.add_error("Could not extract valid Python code from LLM response")
            log_progress("Could not extract valid Python code from LLM response", level="error")
            return False
        
        # Execute code with retries
        log_progress("Executing generated code")
        success, error_info = self.execute_code_with_retries(
            code, input_file, output_file, self.max_attempts
        )
        
        if success:
            # Validate result
            log_progress("Validating processed output")
            if self.validate_result(output_file):
                log_progress("Validation successful")
                return True
            else:
                log_progress("Validation failed", level="error")
                return False
        else:
            self.add_error(f"Code execution failed after {self.max_attempts} attempts")
            log_progress(f"Code execution failed after {self.max_attempts} attempts", level="error")
            return False
    
    def _extract_code(self, llm_response: str) -> Optional[str]:
        """
        Extract Python code from LLM response.
        
        Args:
            llm_response: Full response from the LLM
            
        Returns:
            Extracted Python code or None if extraction failed
        """
        # Look for code blocks
        if "```python" in llm_response and "```" in llm_response:
            # Extract code between Python code blocks
            start_idx = llm_response.find("```python") + 9
            end_idx = llm_response.find("```", start_idx)
            
            if start_idx >= 9 and end_idx > start_idx:
                return llm_response[start_idx:end_idx].strip()
        
        # If no code blocks found, assume the entire response is code
        if "import" in llm_response and ("open(" in llm_response or "read" in llm_response):
            return llm_response.strip()
        
        return None
    
    def execute_code_with_retries(
        self, 
        code: str, 
        input_file: str, 
        output_file: str, 
        max_attempts: int
    ) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Execute Python code with retry mechanism on failure.
        
        Args:
            code: Python code to execute
            input_file: Path to input file referenced in the code
            output_file: Path to output file referenced in the code
            max_attempts: Maximum number of retry attempts
            
        Returns:
            Tuple of (success boolean, error information if failed)
        """
        # Add security note
        log_progress(
            "SECURITY NOTE: Code is being executed directly. "
            "For production use, consider implementing a sandbox environment."
        )
        
        # Initial attempt
        success, error_info = execute_python_code(code, input_file, output_file)
        if success:
            return True, None
        
        # Display error information
        formatted_error = format_error_details(error_info, code)
        log_progress(f"Initial execution failed:\n{formatted_error}", level="error")
        
        # Retry loop
        for attempt in range(1, max_attempts + 1):
            log_progress(f"Retry attempt {attempt}/{max_attempts}")
            
            # Format error for retry prompt
            retry_prompt = ERROR_RETRY_PROMPT.format(
                error_message=error_info.get("error_message", "Unknown error"),
                line_number=error_info.get("line_number", "Unknown"),
                error_line=error_info.get("error_line", ""),
                code=code
            )
            
            # Send to LLM for correction
            try:
                response = self.llm_adapter.send_prompt(retry_prompt, "")
                new_code = self._extract_code(response)
                
                if not new_code:
                    log_progress("Could not extract valid Python code from retry response", level="error")
                    continue
                
                # Execute corrected code
                success, error_info = execute_python_code(new_code, input_file, output_file)
                
                if success:
                    log_progress(f"Execution successful on retry attempt {attempt}")
                    return True, None
                
                # Display error information
                formatted_error = format_error_details(error_info, new_code)
                log_progress(f"Retry {attempt} failed:\n{formatted_error}", level="error")
                
                # Update code for next iteration
                code = new_code
                
            except Exception as e:
                log_progress(f"LLM retry request failed: {str(e)}", level="error")
        
        return False, error_info