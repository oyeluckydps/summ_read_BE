import subprocess
import time
import os

def run_command(command, capture_output=False):
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=capture_output,
            text=True
        )
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {command}\n{e}")
        return None

def start_docker_container(container_name):
    print("[INFO] Starting Docker container...")
    cmd = (
        f"docker run -dit --rm --gpus=all --name {container_name} "
        "mineru:latest /bin/bash"
    )
    run_command(cmd)
    time.sleep(2)

def create_temp_folder_in_container(container_name, folder_path):
    cmd = f"docker exec {container_name} mkdir -p {folder_path}"
    run_command(cmd)

def copy_files_to_container(container_name, local_folder, container_folder):
    cmd = f"docker cp {local_folder}/. {container_name}:{container_folder}/"
    run_command(cmd)

def stop_docker_container(container_name):
    cmd = f"docker stop {container_name}"
    run_command(cmd)
