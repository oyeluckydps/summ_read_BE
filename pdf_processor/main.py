import os
import tempfile
import uuid
from pdf_processor import file_utils, docker_utils, job_runner

def main(input_path):
    if not os.path.exists(input_path):
        print(f"[ERROR] Input path does not exist: {input_path}")
        return

    container_name = f"mineru_{uuid.uuid4().hex[:8]}"
    container_temp_dir = "/tmp/pdfs"

    # Create a local temp folder to prepare files
    with tempfile.TemporaryDirectory() as local_temp_dir:
        renamed_files = file_utils.prepare_pdf_files(input_path, local_temp_dir)

        if not renamed_files:
            print("[ERROR] No PDF files found to process.")
            return

        print(f"[INFO] {len(renamed_files)} PDF file(s) ready for processing.")
        
        docker_utils.start_docker_container(container_name)
        docker_utils.create_temp_folder_in_container(container_name, container_temp_dir)
        docker_utils.copy_files_to_container(container_name, local_temp_dir, container_temp_dir)

        print("[INFO] Starting asynchronous job processing inside container...")
        job_runner.run_jobs_async(container_name, container_temp_dir, renamed_files, input_path)

        print("[INFO] Cleaning up Docker container...")
        docker_utils.stop_docker_container(container_name)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_path_to_pdf_or_folder>")
    else:
        main(sys.argv[1])
