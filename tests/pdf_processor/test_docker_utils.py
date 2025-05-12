import os
import subprocess
import unittest
from unittest.mock import patch, call, MagicMock

# Import the module to test
from pdf_processor.docker_utils import (
    run_command,
    start_docker_container,
    stop_docker_container,
    copy_all_results_from_container
)

class TestDockerUtils(unittest.TestCase):

    @patch('pdf_processor.docker_utils.subprocess.run')
    def test_run_command_without_capture(self, mock_run):
        """Test run_command without capturing output"""
        # Setup mock
        mock_result = MagicMock()
        mock_run.return_value = mock_result
        
        # Call function
        run_command("test command")
        
        # Verify subprocess.run was called correctly
        mock_run.assert_called_once_with("test command", shell=True, check=True, 
                                        capture_output=False, text=True)

    @patch('pdf_processor.docker_utils.subprocess.run')
    def test_run_command_with_capture(self, mock_run):
        """Test run_command with capturing output"""
        # Setup mock
        mock_result = MagicMock()
        mock_result.stdout = "command output\n"
        mock_run.return_value = mock_result
        
        # Call function
        result = run_command("test command", capture_output=True)
        
        # Verify subprocess.run was called correctly
        mock_run.assert_called_once_with("test command", shell=True, check=True, 
                                        capture_output=True, text=True)
        # Verify return value
        self.assertEqual(result, "command output")

    @patch('pdf_processor.docker_utils.subprocess.run')
    def test_run_command_error(self, mock_run):
        """Test run_command when subprocess raises an error"""
        # Setup mock to raise exception
        mock_run.side_effect = subprocess.CalledProcessError(1, "test command")
        
        # Verify exception is raised
        with self.assertRaises(subprocess.CalledProcessError):
            run_command("test command")

    @patch('pdf_processor.docker_utils.run_command')
    @patch('pdf_processor.docker_utils.os.urandom')
    def test_start_docker_container(self, mock_urandom, mock_run_command):
        """Test starting a Docker container"""
        # Setup mocks
        mock_urandom.return_value = b'abcd'
        
        # Call function
        container_name = start_docker_container()
        
        # Verify expected container name
        self.assertEqual(container_name, "mineru_61626364")
        
        # Verify Docker run command was called correctly
        expected_cmd = (
            "docker run -d --gpus=all --name mineru_61626364 mineru_mod:latest "
            "/bin/bash -c 'source ~/.bashrc; while true; do sleep 3600; done' "
        )
        mock_run_command.assert_called_once_with(expected_cmd)

    @patch('pdf_processor.docker_utils.run_command')
    def test_start_docker_container_error(self, mock_run_command):
        """Test error handling when starting a Docker container fails"""
        # Setup mock to raise exception
        mock_run_command.side_effect = subprocess.CalledProcessError(1, "docker run")
        
        # Verify exception is raised
        with self.assertRaises(subprocess.CalledProcessError):
            start_docker_container()

    @patch('pdf_processor.docker_utils.run_command')
    def test_stop_docker_container(self, mock_run_command):
        """Test stopping a Docker container"""
        # Call function
        stop_docker_container("test_container")
        
        # Verify Docker stop command was called correctly
        mock_run_command.assert_called_once_with("docker stop test_container")

    @patch('pdf_processor.docker_utils.run_command')
    def test_stop_docker_container_error(self, mock_run_command):
        """Test error handling when stopping a Docker container fails"""
        # Setup mock to raise exception
        mock_run_command.side_effect = subprocess.CalledProcessError(1, "docker stop")
        
        # Verify exception is raised
        with self.assertRaises(subprocess.CalledProcessError):
            stop_docker_container("test_container")

    @patch('pdf_processor.docker_utils.run_command')
    def test_copy_all_results_from_container(self, mock_run_command):
        """Test copying results from container to host"""
        # Call function
        copy_all_results_from_container(
            "test_container", 
            "/container/path", 
            "/host/path"
        )
        
        # Verify Docker cp command was called correctly
        expected_cmd = "docker cp test_container:/container/path/. /host/path"
        mock_run_command.assert_called_once_with(expected_cmd)

    @patch('pdf_processor.docker_utils.run_command')
    def test_copy_all_results_from_container_error(self, mock_run_command):
        """Test error handling when copying results fails"""
        # Setup mock to raise exception
        mock_run_command.side_effect = subprocess.CalledProcessError(1, "docker cp")
        
        # Verify exception is raised
        with self.assertRaises(subprocess.CalledProcessError):
            copy_all_results_from_container(
                "test_container", 
                "/container/path", 
                "/host/path"
            )

if __name__ == '__main__':
    unittest.main()