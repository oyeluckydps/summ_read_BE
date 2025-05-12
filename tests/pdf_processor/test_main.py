import unittest
from unittest.mock import patch, call, MagicMock
import os
import shutil
import sys

from pdf_processor.main import main

class TestMain(unittest.TestCase):
    
    @patch('pdf_processor.main.docker_utils.stop_docker_container')
    @patch('pdf_processor.main.docker_utils.copy_all_results_from_container')
    @patch('pdf_processor.main.job_runner.monitor_jobs')
    @patch('pdf_processor.main.docker_utils.run_command')
    @patch('pdf_processor.main.docker_utils.start_docker_container')
    @patch('pdf_processor.main.file_utils.prepare_pdf_files')
    @patch('pdf_processor.main.os.makedirs')
    @patch('pdf_processor.main.shutil.rmtree')
    def test_main_with_single_file(self, mock_rmtree, mock_makedirs, mock_prepare_files, 
                                   mock_start_container, mock_run_command, mock_monitor_jobs,
                                   mock_copy_results, mock_stop_container):
        """Test main function with a single PDF file input"""
        # Setup mocks
        mock_start_container.return_value = "test_container"
        mock_prepare_files.return_value = {"test.pdf": "/path/to/test.pdf"}
        
        # Test with a file path
        with patch('pdf_processor.main.os.path.isfile', return_value=True):
            with patch('pdf_processor.main.os.path.isdir', return_value=False):
                with patch('pdf_processor.main.os.path.dirname', return_value="/path/to"):
                    main("/path/to/test.pdf")
        
        # Verify function calls
        mock_makedirs.assert_called_once_with("temp_pdfs", exist_ok=True)
        mock_prepare_files.assert_called_once_with("/path/to/test.pdf", "temp_pdfs")
        mock_start_container.assert_called_once()
        
        # Verify Docker operations
        mock_run_command.assert_has_calls([
            call("docker exec -it test_container mkdir -p /tmp/pdfs"),
            call("docker cp temp_pdfs/. test_container:/tmp/pdfs")
        ])
        
        # Verify job monitoring
        mock_monitor_jobs.assert_called_once_with(
            "test_container", ["test.pdf"], "/tmp/pdfs", None
        )
        
        # Verify results copying and cleanup
        # Key change: Now verify that parent directory (/path/to) is used instead of the file path
        mock_copy_results.assert_called_once_with(
            "test_container", "/tmp/pdfs", "/path/to"
        )
        mock_stop_container.assert_called_once_with("test_container")
        mock_rmtree.assert_called_once_with("temp_pdfs")
    
    @patch('pdf_processor.main.docker_utils.stop_docker_container')
    @patch('pdf_processor.main.docker_utils.copy_all_results_from_container')
    @patch('pdf_processor.main.job_runner.monitor_jobs')
    @patch('pdf_processor.main.docker_utils.run_command')
    @patch('pdf_processor.main.docker_utils.start_docker_container')
    @patch('pdf_processor.main.file_utils.prepare_pdf_files')
    @patch('pdf_processor.main.os.makedirs')
    @patch('pdf_processor.main.shutil.rmtree')
    def test_main_with_directory(self, mock_rmtree, mock_makedirs, mock_prepare_files, 
                                mock_start_container, mock_run_command, mock_monitor_jobs,
                                mock_copy_results, mock_stop_container):
        """Test main function with a directory input"""
        # Setup mocks
        mock_start_container.return_value = "test_container"
        mock_prepare_files.return_value = {
            "test1.pdf": "/path/to/test1.pdf",
            "test2.pdf": "/path/to/test2.pdf"
        }
        
        # Test with a directory path
        with patch('pdf_processor.main.os.path.isfile', return_value=False):
            with patch('pdf_processor.main.os.path.isdir', return_value=True):
                main("/path/to/pdf_dir")
        
        # Verify function calls
        mock_makedirs.assert_called_once_with("temp_pdfs", exist_ok=True)
        mock_prepare_files.assert_called_once_with("/path/to/pdf_dir", "temp_pdfs")
        mock_start_container.assert_called_once()
        
        # Verify job monitoring for multiple files
        mock_monitor_jobs.assert_called_once()
        # Get the actual arguments passed to monitor_jobs
        args, _ = mock_monitor_jobs.call_args
        container_name, pdf_files, container_dir, callback = args
        
        # Verify the arguments
        self.assertEqual(container_name, "test_container")
        self.assertEqual(set(pdf_files), {"test1.pdf", "test2.pdf"})
        self.assertEqual(container_dir, "/tmp/pdfs")
        self.assertIsNone(callback)
        
        # Verify cleanup
        # For directories, the original directory path should still be used
        mock_copy_results.assert_called_once_with(
            "test_container", "/tmp/pdfs", "/path/to/pdf_dir"
        )
        mock_stop_container.assert_called_once_with("test_container")
        mock_rmtree.assert_called_once_with("temp_pdfs")
    
    @patch('pdf_processor.main.file_utils.prepare_pdf_files')
    @patch('pdf_processor.main.os.makedirs')    
    def test_main_with_no_pdfs(self, mock_makedirs, mock_prepare_files):
        """Test main function when no PDF files are found"""
        # Setup mocks
        mock_prepare_files.return_value = {}  # No PDFs found
        
        # Test with a directory path
        with patch('pdf_processor.main.os.path.isfile', return_value=False):
            with patch('pdf_processor.main.os.path.isdir', return_value=True):
                main("/path/to/empty_dir")
        
        # Verify early return when no PDFs are found
        mock_makedirs.assert_called_once()
        mock_prepare_files.assert_called_once()
    
    @patch('pdf_processor.main.os.path.isfile', return_value=False)
    @patch('pdf_processor.main.os.path.isdir', return_value=False)
    def test_main_with_invalid_path(self, mock_isdir, mock_isfile):
        """Test main function with an invalid input path"""
        main("/invalid/path")
        
        # Verify path checks
        mock_isfile.assert_called_once()
        mock_isdir.assert_called_once()
        
def test_command_line_interface(self):
    """Test the command line interface with arguments"""
    from pdf_processor.main import run_from_command_line
    
    with patch('pdf_processor.main.main') as mock_main:
        # Call with arguments
        result = run_from_command_line(['main.py', '/path/to/input'])
        
        # Verify main was called with correct argument
        mock_main.assert_called_once_with('/path/to/input')
        self.assertEqual(result, 0)  # Check success return code

def test_command_line_interface_no_args(self):
    """Test the command line interface with no arguments"""
    from pdf_processor.main import run_from_command_line
    
    with patch('pdf_processor.main.main') as mock_main:
        # Call with no arguments
        result = run_from_command_line(['main.py'])
        
        # Verify main was not called
        mock_main.assert_not_called()
        self.assertEqual(result, 1)  # Check error return code