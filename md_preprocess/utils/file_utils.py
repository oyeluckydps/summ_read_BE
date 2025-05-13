"""
File utilities for MD Preprocess library.
"""

import os
import uuid
import shutil
import difflib
from typing import Optional


def copy_with_uuid(
    input_file: str, 
    output_dir: str, 
    prefix: str = "to_correct_", 
    session_id: Optional[str] = None
) -> str:
    """
    Copy a file to the output directory with UUID in the filename.
    
    Args:
        input_file: Path to the input file
        output_dir: Directory to copy to
        prefix: Prefix to use for the new filename
        session_id: Optional session ID to use instead of generating a new UUID
        
    Returns:
        Path to the copied file
    """
    # Create output directory if it doesn't exist
    ensure_directory_exists(output_dir)
    
    # Generate UUID if not provided
    file_id = session_id or str(uuid.uuid4())
    
    # Get file extension
    _, ext = os.path.splitext(input_file)
    
    # Create new filename
    new_filename = f"{prefix}{file_id}{ext}"
    output_path = os.path.join(output_dir, new_filename)
    
    # Copy file
    shutil.copy2(input_file, output_path)
    
    return output_path


def calculate_diff_percentage(file1: str, file2: str) -> float:
    """
    Calculate the percentage difference between two files.
    
    Args:
        file1: Path to the first file
        file2: Path to the second file
        
    Returns:
        Percentage difference as a float (0-100)
    """
    try:
        with open(file1, 'r', encoding='utf-8') as f:
            content1 = f.readlines()
        with open(file2, 'r', encoding='utf-8') as f:
            content2 = f.readlines()
            
        # Calculate difference ratio using difflib
        matcher = difflib.SequenceMatcher(None, content1, content2)
        similarity = matcher.ratio()
        
        # Convert to percentage difference
        diff_percentage = (1 - similarity) * 100
        
        return diff_percentage
        
    except Exception as e:
        print(f"Error calculating diff: {str(e)}")
        return 0.0


def ensure_directory_exists(directory: str) -> None:
    """
    Ensure a directory exists, creating it if needed.
    
    Args:
        directory: Path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)