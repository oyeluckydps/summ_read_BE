import subprocess
import os
import shutil

def run_command(cmd, capture_output=False):
    """Executes a shell command and optionally captures output."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=capture_output, text=True)
        if capture_output:
            return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {cmd} - {e}")
        raise

def start_docker_container():
    """Starts a Docker container and returns its name."""

    container_name = f"mineru_{os.urandom(4).hex()}"
    try:
        run_command(f"docker run -d --gpus=all --name {container_name} mineru_mod:latest /bin/bash -c 'source ~/.bashrc; while true; do sleep 3600; done' ")
        return container_name
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to start Docker container.")
        raise

def stop_docker_container(container_name: str):
    """Stops a Docker container."""
    try:
        run_command(f"docker stop {container_name}")
    except subprocess.CalledProcessError:
        print(f"[ERROR] Failed to stop Docker container: {container_name}")
        raise

def copy_all_results_from_container(container_name: str, container_temp_dir: str, host_output_dir: str):
    """Copies all output folders from the container's temp directory to the host."""
    try:
        run_command(f"docker cp {container_name}:{container_temp_dir}/. {host_output_dir}")
        print(f"[INFO] Successfully copied all results from container to {host_output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to copy results from container: {e}")
        raise

