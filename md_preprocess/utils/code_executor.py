"""
Code execution utilities for MD Preprocess library.
"""

import os
import sys
import traceback
from io import StringIO
from typing import Dict, Any, Optional, Tuple


def execute_python_code(
    code: str, 
    input_file: str, 
    output_file: str
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Execute Python code safely and capture errors.
    
    Args:
        code: Python code to execute
        input_file: Path to input file referenced in the code
        output_file: Path to output file referenced in the code
        
    Returns:
        Tuple of (success boolean, error information if failed)
    """
    # SECURITY NOTE: This function executes code directly, which could be a security risk.
    # For production use, consider implementing a sandbox environment or other security measures.
    
    # Create error information dictionary
    error_info = {
        "error_message": None,
        "line_number": None,
        "error_line": None,
        "traceback": None
    }
    
    # Redirect stdout and stderr
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = stdout_capture = StringIO()
    sys.stderr = stderr_capture = StringIO()
    
    try:
        # Execute the code
        env = {}
        exec(code, env, env)
        
        # Check if output file was created
        if not os.path.exists(output_file):
            error_info["error_message"] = "Output file was not created"
            return False, error_info
            
        return True, None
        
    except Exception as e:
        # Get exception information
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        # Extract line number and error line
        tb = traceback.extract_tb(exc_traceback)
        if tb:
            # Find the frame that refers to the executed code
            for frame in tb:
                if frame.filename == "<string>":
                    line_number = frame.lineno
                    break
            else:
                line_number = 0
                
            # Get code lines
            code_lines = code.split("\n")
            
            # Extract the error line
            if 0 <= line_number - 1 < len(code_lines):
                error_line = code_lines[line_number - 1]
            else:
                error_line = ""
                
            error_info.update({
                "error_message": str(e),
                "line_number": line_number,
                "error_line": error_line,
                "traceback": traceback.format_exc()
            })
        
        return False, error_info
        
    finally:
        # Restore stdout and stderr
        sys.stdout, sys.stderr = old_stdout, old_stderr
        
        # Get output from stdout and stderr
        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()
        
        if error_info["error_message"] is not None:
            error_info.update({
                "stdout": stdout_output,
                "stderr": stderr_output
            })


def format_error_details(error_info: Dict[str, Any], code: str) -> str:
    """
    Format error details with line numbers and context for display.
    
    Args:
        error_info: Error information dictionary
        code: Code that produced the error
        
    Returns:
        Formatted error details string
    """
    if not error_info:
        return "Unknown error"
        
    # Extract error information
    error_message = error_info.get("error_message", "Unknown error")
    line_number = error_info.get("line_number", 0)
    error_line = error_info.get("error_line", "")
    
    # Create formatted error message
    formatted_error = f"Error: {error_message}\n"
    formatted_error += f"Line {line_number}: {error_line}\n\n"
    
    # Add context from the code
    code_lines = code.split("\n")
    if 0 <= line_number - 1 < len(code_lines):
        # Add lines before and after the error for context
        start_line = max(0, line_number - 3)
        end_line = min(len(code_lines), line_number + 2)
        
        formatted_error += "Code context:\n"
        for i in range(start_line, end_line):
            prefix = ">" if i == line_number - 1 else " "
            line_num = i + 1
            formatted_error += f"{prefix} {line_num:4d} | {code_lines[i]}\n"
    
    return formatted_error