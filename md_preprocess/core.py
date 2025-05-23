"""
Core module for MD Preprocess library.
"""

import os
import uuid
import logging
import shutil
from typing import Optional, Dict, Any

from md_preprocess.preprocessors.base import BasePreprocessor
from md_preprocess.preprocessors.llm_1step_code import LLM1StepCode
from md_preprocess.llm.claude_adapter import ClaudeAdapter
from md_preprocess.utils.file_utils import copy_with_uuid, calculate_diff_percentage, ensure_directory_exists
from md_preprocess.utils.logging_utils import log_progress
from md_preprocess.config import DEFAULT_MAX_ATTEMPTS, DEFAULT_LLM


class MDPreprocessManager:
    """
    Main class that orchestrates the preprocessing workflow for markdown files.
    """
    
    def __init__(
        self, 
        input_file: str, 
        output_dir: str,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        llm_name: Optional[str] = DEFAULT_LLM,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the MD Preprocess Manager.
        
        Args:
            input_file: Path to the input markdown file
            output_dir: Directory for final output file
            max_attempts: Maximum number of retry attempts for code execution
            llm_name: Name of the LLM service to use
            api_key: API key for the LLM service
            **kwargs: Additional configuration options
        """
        self.input_file = input_file
        self.output_dir = output_dir  # This is now the final output directory
        self.temp_dir = "temp_preprocess"  # Always use temp_preprocess for working files
        self.max_attempts = max_attempts
        self.llm_name = llm_name
        self.api_key = api_key
        self.config = kwargs
        
        # Set up directories
        ensure_directory_exists(self.output_dir)
        ensure_directory_exists(self.temp_dir)
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger("md_preprocess")
        
        # Generate a unique ID for this processing session
        self.session_id = str(uuid.uuid4())
        
        # Initialize the preprocessor
        self.preprocessor = self._initialize_preprocessor()
    
    def _initialize_preprocessor(self) -> BasePreprocessor:
        """
        Initialize the appropriate preprocessor based on configuration.
        
        Returns:
            An instance of a BasePreprocessor subclass
        """
        llm_adapter = None
        
        if self.llm_name == "claude":
            # Initialize Claude adapter
            llm_adapter = ClaudeAdapter(
                api_key=self.api_key,
                model="claude-3-7-sonnet-20250219",
                use_cache=self.config.get("use_cache", True)
            )
        else:
            # Default to Claude
            self.logger.warning(f"LLM '{self.llm_name}' not supported. Using Claude as default.")
            llm_adapter = ClaudeAdapter(
                api_key=self.api_key,
                model="claude-3-7-sonnet-20250219",
                use_cache=self.config.get("use_cache", True)
            )
        
        # Create and return the LLM1StepCode preprocessor
        return LLM1StepCode(
            llm_adapter=llm_adapter,
            max_attempts=self.max_attempts
        )
    
    def process(self) -> Dict[str, Any]:
        """
        Execute the main processing workflow.
        
        Returns:
            Dictionary containing processing results and statistics
        """
        log_progress("Starting preprocessing workflow")
        
        try:
            # Copy input file to temp working directory with UUID
            temp_input_file = copy_with_uuid(
                self.input_file, 
                self.temp_dir, 
                prefix="to_correct_", 
                session_id=self.session_id
            )
            log_progress(f"Copied input file to {temp_input_file}")
            
            # Define temp output file path (within temp directory)
            temp_output_file = os.path.join(
                self.temp_dir, 
                f"corrected_{self.session_id}.md"
            )
            
            # Run the preprocessor
            log_progress("Running preprocessor")
            success = self.preprocessor.preprocess(temp_input_file, temp_output_file)
            
            if success:
                # Calculate statistics before moving the file
                log_progress("Preprocessing completed successfully")
                stats = self.report_statistics(self.input_file, temp_output_file)
                
                # Copy the output file to the final output directory
                input_filename = os.path.basename(self.input_file)
                base_name, _ = os.path.splitext(input_filename)
                final_output_file = os.path.join(self.output_dir, f"{base_name}_corrected.md")
                
                shutil.copy2(temp_output_file, final_output_file)
                log_progress(f"Copied final output to {final_output_file}")
                
                # Clean up temporary files
                self._cleanup_temp_files()
                
                return {
                    "success": True,
                    "output_file": final_output_file,
                    "statistics": stats
                }
            else:
                log_progress("Preprocessing failed", level="error")
                # Clean up temporary files even on failure
                self._cleanup_temp_files()
                
                return {
                    "success": False,
                    "output_file": None,
                    "errors": self.preprocessor.get_errors()
                }
                
        except Exception as e:
            log_progress(f"Error during processing: {str(e)}", level="error")
            # Make sure to clean up temporary files on exception
            self._cleanup_temp_files()
            
            return {
                "success": False,
                "output_file": None,
                "errors": [str(e)]
            }
    
    def _cleanup_temp_files(self) -> None:
        """
        Clean up temporary files created during processing.
        """
        try:
            # Find all files with this session ID
            temp_input_pattern = f"to_correct_{self.session_id}"
            temp_output_pattern = f"corrected_{self.session_id}"
            
            for filename in os.listdir(self.temp_dir):
                if temp_input_pattern in filename or temp_output_pattern in filename:
                    file_path = os.path.join(self.temp_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        log_progress(f"Removed temporary file: {file_path}")
            
            log_progress("Cleaned up all temporary files")
            
        except Exception as e:
            log_progress(f"Error cleaning up temporary files: {str(e)}", level="warning")
    
    def report_statistics(self, original_file: str, processed_file: str) -> Dict[str, Any]:
        """
        Calculate and display statistics about the preprocessing.
        
        Args:
            original_file: Path to the original input file
            processed_file: Path to the processed output file
            
        Returns:
            Dictionary of statistics
        """
        diff_percent = calculate_diff_percentage(original_file, processed_file)
        
        # Get file sizes
        original_size = os.path.getsize(original_file)
        processed_size = os.path.getsize(processed_file)
        size_diff = processed_size - original_size
        
        stats = {
            "diff_percentage": diff_percent,
            "original_size": original_size,
            "processed_size": processed_size,
            "size_difference": size_diff
        }
        
        # Log statistics
        log_progress(f"Difference between files: {diff_percent:.2f}%")
        log_progress(f"Original size: {original_size} bytes, Processed size: {processed_size} bytes")
        
        return stats