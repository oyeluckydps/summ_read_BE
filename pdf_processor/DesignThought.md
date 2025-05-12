# DesignThought.md

## 1. Purpose and Rationale

This folder contains a modular Python project designed to process one or multiple PDF files using a Docker containerized workflow. The goal is to automate the preprocessing, execution, and result collection of a script (`call_job.sh`) that must run inside a GPU-enabled Docker container (`mineru:latest`).

### Updated Design Overview:

1. **Input Handling**: The user provides either a single PDF or a directory of PDFs.
2. **PDF Preparation**:
   - Files are sanitized (renamed to remove problematic characters).
   - Sanitized copies are stored in a temporary local folder.
3. **Docker Setup**:
   - A Docker container is started with a known name and GPU support.
   - A temporary directory (`/tmp/pdfs`) is created inside the container.
4. **Transfer to Container**:
   - All prepared PDFs are copied into the container's temp directory.
5. **Job Execution**:
   - The script `call_job.sh` is invoked for each file inside the container.
   - Job outputs are generated into a folder named after the input PDF.
6. **Result Collection**:
   - Once all jobs are completed, results are copied back from the container to the same directory as the original input.
7. **Cleanup**:
   - The Docker container is stopped and removed.
   - Temporary folders are deleted from the host.

> ⚠️ Note: Unlike earlier versions, this implementation uses **synchronous job execution**. Jobs are run one after another for simplicity and predictability.

---

## 2. LLM Prompt to Reproduce This Code

You can recreate this system by giving the following prompt to an LLM:

> "Build a modular Python project that:
> 1. Takes an input path (a PDF file or a folder of PDFs).
> 2. Copies and renames the PDFs (removing special characters) into a temporary folder.
> 3. Starts a Docker container (e.g., `mineru:latest`) with GPU support.
> 4. Creates a temporary directory inside the container and copies all PDFs into it.
> 5. For each PDF, synchronously runs a shell script (`call_job.sh`) inside the container.
> 6. After all jobs complete, copies the result folders (named after each PDF) from container to host.
> 7. Stops and removes the container after use.
> 8. Includes modular scripts: `main.py` (orchestrator), `file_utils.py` (file ops), `docker_utils.py` (Docker ops), `job_runner.py` (job handler).
> 9. Ensure proper logging, error checks, and cleanup."

---

## 3. File and Function Breakdown

### `main.py`
**Role**: Main controller script.

- `main(input_path)`: Orchestrates the pipeline.
  - Handles path validation (file/folder).
  - Uses `file_utils.prepare_pdf_files` to prepare sanitized copies.
  - Starts Docker container using `docker_utils`.
  - Transfers PDFs and triggers `job_runner.monitor_jobs` to process files synchronously.
  - Copies back results and performs cleanup.

---

### `file_utils.py`
**Role**: File sanitization and preparation.

- `sanitize_filename(filename)`: Replaces all characters except alphanumerics, underscores, and hyphens with underscores.
- `prepare_pdf_files(input_path, destination_folder)`: 
  - Identifies `.pdf` files.
  - Copies them to a destination folder with sanitized names.
  - Returns a dictionary mapping sanitized names to original paths.

---

### `docker_utils.py`
**Role**: Docker command execution and file transfer.

- `run_command(cmd, capture_output=False)`: Runs shell commands and optionally returns output.
- `start_docker_container()`: Launches a GPU-enabled container with a generated name.
- `stop_docker_container(container_name)`: Stops and removes the running container.
- `copy_all_results_from_container(container_name, container_path, host_output_path)`: Pulls processed result folders back to host.

---

### `job_runner.py`
**Role**: Synchronous execution of processing jobs.

- `monitor_jobs(container_name, pdf_filenames, container_temp_dir, callback=None)`:
  - Iterates over all PDFs.
  - Executes the container script `call_job.sh` with appropriate arguments for each file.
  - Monitors and prints real-time output line by line.
  - After each job, checks if result folder exists and copies it back using `docker cp`.

---

This document serves as a comprehensive yet concise reference. It supports onboarding for human developers and also functions as a rich seed prompt for LLM-based code regeneration or documentation.
