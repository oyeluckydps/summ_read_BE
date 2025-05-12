import os
import sys
import shutil
from pdf_processor import file_utils, docker_utils, job_runner

def main(input_path):
    # Prepare file paths (handle both single file or folder input)
    if os.path.isfile(input_path):
        temp_dir = "temp_pdfs"
        os.makedirs(temp_dir, exist_ok=True)
        renamed_files = file_utils.prepare_pdf_files(input_path, temp_dir)
        pdf_files = list(renamed_files.keys())
    elif os.path.isdir(input_path):
        temp_dir = "temp_pdfs"
        os.makedirs(temp_dir, exist_ok=True)
        renamed_files = file_utils.prepare_pdf_files(input_path, temp_dir)
        pdf_files = list(renamed_files.keys())
    else:
        print("[ERROR] Invalid input path")
        return

    if not pdf_files:
        print("[INFO] No PDF files found to process.")
        return

    print(f"[INFO] {len(pdf_files)} PDF file(s) ready for processing.")

    # Start a single Docker container
    container_name = docker_utils.start_docker_container()
    container_temp_dir = "/tmp/pdfs"

    # Create temp dir in container and copy files
    docker_utils.run_command(f"docker exec -it {container_name} mkdir -p {container_temp_dir}")
    docker_utils.run_command(f"docker cp temp_pdfs/. {container_name}:{container_temp_dir}")

    # Process all jobs in the container
    print("[INFO] Processing all jobs inside the container...")
    job_runner.monitor_jobs(container_name, pdf_files, container_temp_dir, None)  # No callback needed here

    # Copy results back from the container
    print("[INFO] Copying results back from the container...")
    docker_utils.copy_all_results_from_container(container_name, container_temp_dir, input_path)

    # Stop and remove the container
    docker_utils.stop_docker_container(container_name)

    # Cleanup temporary directory
    shutil.rmtree(temp_dir)
    print("[INFO] Temporary files cleaned up.")

def run_from_command_line(args=None):
    """Run the application from command line arguments."""
    if args is None:
        args = sys.argv
    
    if len(args) != 2:
        print("[ERROR] Please provide the input path (file or folder).")
        return 1  # Exit code
    
    input_path = args[1]
    main(input_path)
    return 0  # Success

if __name__ == "__main__":
    sys.exit(run_from_command_line())

