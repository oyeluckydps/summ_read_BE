import os
import subprocess
from pdf_processor.file_utils import get_output_folder_name

def run_job_in_container(container_name: str, pdf_file: str, temp_dir: str):
    output_folder = get_output_folder_name(pdf_file)
    pdf_path = f"{temp_dir}/{pdf_file}"
    print(f"[INFO] Starting job: {pdf_file}")

    try:
        # Run the job using subprocess

        process = subprocess.run(
            ["docker", "exec", container_name, "/bin/bash", "-c",
            f"export PATH=\"/opt/mineru_venv/bin:$PATH\" && /call_job.sh \"{pdf_path}\" \"{temp_dir}\""],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        if process.stdout:
            print(f"[{pdf_file}] {process.stdout.strip()}")
        if process.stderr:
            print(f"[{pdf_file} - ERROR] {process.stderr.strip()}")

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to process {pdf_file} (subprocess error): {e}")
    except FileNotFoundError as e:
        print(f"[ERROR] Failed to process {pdf_file} (file not found): {e}")
    except Exception as e:
        print(f"[ERROR] Failed to process {pdf_file}: {e}")


def monitor_jobs(container_name: str, pdf_files: list[str], temp_dir: str, callback=None):
    """
    Run jobs one by one for all the PDF files in the list.
    """
    for pdf_file in pdf_files:
        run_job_in_container(container_name, pdf_file, temp_dir)

