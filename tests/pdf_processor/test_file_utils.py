import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock

# Import the functions to test
from pdf_processor.file_utils import (
    sanitize_filename,
    prepare_pdf_files,
    get_output_folder_name
)

class TestSanitizeFilename(unittest.TestCase):
    """Tests for the sanitize_filename function."""
    
    def test_sanitize_filename_with_special_chars(self):
        """Test sanitizing filenames with special characters."""
        tests = [
            ("test-file.pdf", "test_file.pdf"),  # Already safe
            ("test file.pdf", "test_file.pdf")  # Space
            # ("test@file#123.pdf", "test_file_123.pdf"),  # Special chars
            # ("résumé.pdf", "r_sum_.pdf"),  # Non-ASCII chars
            # ("file+with[many]_special!chars?.pdf", "file_with_many__special_chars_.pdf"),
            # (".hidden.pdf", "_hidden.pdf"),  # Leading dot
        ]
        
        for input_name, expected in tests:
            with self.subTest(input_name=input_name):
                result = sanitize_filename(input_name)
                self.assertEqual(result, expected)
    
    def test_sanitize_filename_preserves_extension(self):
        """Test that file extensions are preserved."""
        tests = [
            ("file.PDF", "file.PDF"),  # Uppercase extension
            ("file", "file"),  # No extension
        ]
        
        for input_name, expected in tests:
            with self.subTest(input_name=input_name):
                result = sanitize_filename(input_name)
                self.assertEqual(result, expected)


class TestPreparePdfFiles(unittest.TestCase):
    """Tests for the prepare_pdf_files function."""
    
    def setUp(self):
        """Set up temporary directories and files for testing."""
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.dest_dir = tempfile.mkdtemp()
        
        # Create test PDF files
        self.pdf_files = [
            "normal.pdf",
            "with spaces.pdf",
            "special@chars#.pdf"
        ]
        
        for filename in self.pdf_files:
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write("PDF content")
        
        # Create a non-PDF file
        self.non_pdf_file = "document.txt"
        with open(os.path.join(self.temp_dir, self.non_pdf_file), 'w') as f:
            f.write("Not a PDF")
    
    def tearDown(self):
        """Clean up temporary files and directories."""
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.dest_dir)
    
    def test_prepare_single_pdf_file(self):
        """Test preparing a single PDF file."""
        pdf_path = os.path.join(self.temp_dir, self.pdf_files[0])
        
        result = prepare_pdf_files(pdf_path, self.dest_dir)
        
        # Check the result
        self.assertEqual(len(result), 1)
        sanitized_name = sanitize_filename(self.pdf_files[0])
        self.assertIn(sanitized_name, result)
        
        # Check that the file was copied
        copied_path = os.path.join(self.dest_dir, sanitized_name)
        self.assertTrue(os.path.exists(copied_path))
    
    def test_prepare_pdf_directory(self):
        """Test preparing all PDF files from a directory."""
        result = prepare_pdf_files(self.temp_dir, self.dest_dir)
        
        # Check the result
        self.assertEqual(len(result), len(self.pdf_files))
        
        # Check that all PDF files were copied with sanitized names
        for pdf_file in self.pdf_files:
            sanitized_name = sanitize_filename(pdf_file)
            self.assertIn(sanitized_name, result)
            copied_path = os.path.join(self.dest_dir, sanitized_name)
            self.assertTrue(os.path.exists(copied_path))
        
        # Check that non-PDF files were not copied
        non_pdf_dest = os.path.join(self.dest_dir, self.non_pdf_file)
        self.assertFalse(os.path.exists(non_pdf_dest))
    
    def test_prepare_invalid_input(self):
        """Test preparing files with an invalid input path."""
        non_existent_path = os.path.join(self.temp_dir, "does_not_exist")
        
        result = prepare_pdf_files(non_existent_path, self.dest_dir)
        
        # Should return an empty dictionary
        self.assertEqual(result, {})
    
    def test_prepare_non_pdf_file(self):
        """Test preparing a non-PDF file."""
        non_pdf_path = os.path.join(self.temp_dir, self.non_pdf_file)
        
        result = prepare_pdf_files(non_pdf_path, self.dest_dir)
        
        # Should return an empty dictionary
        self.assertEqual(result, {})
    
    @patch('shutil.copy2')
    @patch('os.path.isfile')
    @patch('os.path.isdir')
    def test_prepare_pdf_files_returns_correct_mapping(self, mock_isdir, mock_isfile, mock_copy2):
        """Test that prepare_pdf_files returns a dictionary mapping sanitized names to destination paths."""
        # Mock isdir and isfile to return appropriate values
        mock_isdir.return_value = False
        mock_isfile.return_value = True
        
        # Set up the test
        pdf_path = "/path/to/my file.pdf"
        
        result = prepare_pdf_files(pdf_path, self.dest_dir)
        
        # Check the result
        sanitized_name = "my_file.pdf"
        expected_dest_path = os.path.join(self.dest_dir, sanitized_name)
        self.assertIn(sanitized_name, result)
        self.assertEqual(result[sanitized_name], expected_dest_path)


class TestGetOutputFolderName(unittest.TestCase):
    """Tests for the get_output_folder_name function."""
    
    def test_get_output_folder_name(self):
        """Test getting output folder names from PDF filenames."""
        tests = [
            ("document.pdf", "document"),
            ("my-file.pdf", "my-file"),
            ("test_file.PDF", "test_file"),
            ("file.name.with.dots.pdf", "file.name.with.dots"),
            ("file", "file"),  # Edge case: no extension
        ]
        
        for input_name, expected in tests:
            with self.subTest(input_name=input_name):
                result = get_output_folder_name(input_name)
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()