"""
Base preprocessor class for MD Preprocess library.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict


class BasePreprocessor(ABC):
    """
    Abstract base class for all preprocessors.
    """
    
    def __init__(self):
        """
        Initialize the base preprocessor.
        """
        self._errors = []
    
    @abstractmethod
    def preprocess(self, input_file: str, output_file: str) -> bool:
        """
        Preprocess the input file and write results to output file.
        
        Args:
            input_file: Path to the input markdown file
            output_file: Path where the output should be written
            
        Returns:
            Boolean indicating success or failure
        """
        pass
    
    def validate_result(self, output_file: str) -> bool:
        """
        Validate the preprocessed output file.
        
        Args:
            output_file: Path to the output file to validate
            
        Returns:
            Boolean indicating whether the output is valid
        """
        # Basic validation - check if file exists and is not empty
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not content.strip():
                self._errors.append("Output file is empty")
                return False
                
            return True
            
        except Exception as e:
            self._errors.append(f"Output validation error: {str(e)}")
            return False
    
    def add_error(self, error: str) -> None:
        """
        Add an error to the error list.
        
        Args:
            error: Error message to add
        """
        self._errors.append(error)
    
    def get_errors(self) -> List[str]:
        """
        Get all errors encountered during preprocessing.
        
        Returns:
            List of error messages
        """
        return self._errors