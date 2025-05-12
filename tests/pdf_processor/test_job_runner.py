import unittest
from unittest.mock import patch, call, MagicMock
import subprocess

from pdf_processor.job_runner import run_job_in_container, monitor_jobs
from pdf_processor.file_utils import get_output_folder_name

class TestJobRunner(unittest.TestCase):
    
    @patch('pdf_processor.job_runner.subprocess.run')
    def test_run_job_in_container_success(self, mock_run):
        """Test running a job in a container successfully"""
        mock_process = MagicMock()
        mock_process.stdout = "Job output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        run_job_in_container("test_container", "test.pdf", "/tmp/pdfs")
        
        mock_run.assert_called_once_with(
            ["docker", "exec", "test_container", "/bin/bash", "-c",
             'export PATH="/opt/mineru_venv/bin:$PATH" && /call_job.sh "/tmp/pdfs/test.pdf" "/tmp/pdfs"'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
    
    @patch('pdf_processor.job_runner.subprocess.run')
    def test_run_job_in_container_with_stderr(self, mock_run):
        """Test running a job that produces stderr output"""
        mock_process = MagicMock()
        mock_process.stdout = "Job output"
        mock_process.stderr = "Error message"
        mock_run.return_value = mock_process
        
        run_job_in_container("test_container", "test.pdf", "/tmp/pdfs")
        
        mock_run.assert_called_once()
    
    @patch('pdf_processor.job_runner.subprocess.run')
    def test_run_job_in_container_subprocess_error(self, mock_run):
        """Test handling subprocess error when running a job"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker exec")
        
        # This should not raise an exception as it's handled internally
        run_job_in_container("test_container", "test.pdf", "/tmp/pdfs")
        
        mock_run.assert_called_once()
    
    @patch('pdf_processor.job_runner.subprocess.run')
    def test_run_job_in_container_file_not_found(self, mock_run):
        """Test handling file not found error when running a job"""
        mock_run.side_effect = FileNotFoundError("No such file")
        
        # This should not raise an exception as it's handled internally
        run_job_in_container("test_container", "test.pdf", "/tmp/pdfs")
        
        mock_run.assert_called_once()
    
    @patch('pdf_processor.job_runner.run_job_in_container')
    def test_monitor_jobs(self, mock_run_job):
        """Test monitoring multiple jobs"""
        pdf_files = ["file1.pdf", "file2.pdf", "file3.pdf"]
        
        monitor_jobs("test_container", pdf_files, "/tmp/pdfs")
        
        expected_calls = [
            call("test_container", "file1.pdf", "/tmp/pdfs"),
            call("test_container", "file2.pdf", "/tmp/pdfs"),
            call("test_container", "file3.pdf", "/tmp/pdfs")
        ]
        mock_run_job.assert_has_calls(expected_calls)
        self.assertEqual(mock_run_job.call_count, 3)
    
    @patch('pdf_processor.job_runner.run_job_in_container')
    def test_monitor_jobs_with_callback(self, mock_run_job):
        """Test monitoring jobs with a callback function"""
        pdf_files = ["file1.pdf", "file2.pdf"]
        callback_mock = MagicMock()
        
        # Note: The current implementation doesn't actually use the callback
        monitor_jobs("test_container", pdf_files, "/tmp/pdfs", callback=callback_mock)
        
        expected_calls = [
            call("test_container", "file1.pdf", "/tmp/pdfs"),
            call("test_container", "file2.pdf", "/tmp/pdfs")
        ]
        mock_run_job.assert_has_calls(expected_calls)
        self.assertEqual(mock_run_job.call_count, 2)
        # In the current implementation, callback is not used
        callback_mock.assert_not_called()