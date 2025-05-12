# DesignThought.md

## 1. Purpose and Rationale

This folder contains a modular Python project designed to process one or multiple PDF files using a Docker containerized workflow. The core motivation is to automate the preprocessing, processing, and postprocessing of PDF files through a custom script (`call_job.sh`) that must run inside a GPU-enabled Docker container (`mineru:latest`).

### Overview of the Process:

1. **Input Handling**: The script accepts a path — either a single PDF or a folder containing multiple PDFs.
2. **PDF Preparation**: All PDF files are copied to a temporary folder, renamed to remove special characters, and prepared for container execution.
3. **Docker Environment Setup**:
   - A Docker container is launched with GPU support.
   - A temporary directory inside the container is created to host the PDF files.
4. **File Transfer to Container**: Prepared PDF files are copied into the container.
5. **Job Execution**:
   - The script `call_job.sh` is run on each PDF inside the container.
   - Jobs are run asynchronously so that outputs are processed and copied back as soon as available.
6. **Post-Processing**:
   - For each completed job, the generated folder (named after the PDF) is copied back to the host machine — either next to the original PDF or in the input folder.

This design ensures efficient, asynchronous job processing, real-time progress reporting, and modular structure for maintenance and scaling.

---

## 2. LLM Prompt to Reproduce This Code

You can reproduce this codebase by prompting an LLM with the following instructions:

> "Create a modular Python project that:
> 1. Accepts a path as input (a PDF file or folder of PDFs).
> 2. Copies and renames all PDFs to remove special characters, storing them in a temp folder.
> 3. Launches a Docker container (e.g., `mineru:latest`) with GPU support using a unique name.
> 4. Creates a temp directory inside the container and copies the sanitized PDFs into it.
> 5. For each PDF, runs a shell script (`call_job.sh`) with the PDF path and output folder as arguments.
> 6. Executes jobs asynchronously and relays real-time output to the user.
> 7. As soon as a job finishes, copies the output folder (named after the PDF) from container to host.
> 8. Includes modular Python files: main.py (controller), file_utils.py (file ops), docker_utils.py (docker ops), job_runner.py (job logic).
> 9. Use good logging, error handling, and comments/documentation throughout the code."

---

## 3. File and Function Breakdown

### `main.py`
**Role**: Entry point for the whole process.
- `main(input_path)`: Orchestrates the full pipeline — prepares files, launches Docker, transfers files, initiates job running, and performs cleanup.

### `file_utils.py`
**Role**: Handles file preparation and sanitization.
- `sanitize_filename(filename)`: Replaces all special characters (except underscores) with underscores.
- `prepare_pdf_files(input_path, destination_folder)`: Copies and renames PDFs to a temp folder and returns a mapping of sanitized to original paths.

### `docker_utils.py`
**Role**: Wraps all Docker-related operations.
- `run_command(cmd, capture_output=False)`: Executes shell commands with error handling.
- `start_docker_container(container_name)`: Launches a GPU-enabled Docker container.
- `create_temp_folder_in_container(container_name, folder_path)`: Makes a directory in the container.
- `copy_files_to_container(container_name, local_folder, container_folder)`: Copies prepared files into the container.
- `stop_docker_container(container_name)`: Gracefully stops the container after processing.

### `job_runner.py`
**Role**: Manages job execution asynchronously.
- `run_single_job(container_name, container_temp_dir, filename, original_path)`: Executes `call_job.sh` for one PDF, monitors output, and copies back result.
- `run_jobs_async(...)`: Runs all jobs concurrently using asyncio.

---

This document serves as both a technical explanation for developers and a reference for LLMs to reconstruct the system design and function accurately.
