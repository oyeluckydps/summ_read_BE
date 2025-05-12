# PDF Processor with Docker Execution

This project automates the processing of PDF files inside a GPU-enabled Docker container. It takes a PDF file or a folder of PDFs as input, renames and transfers them into the container, and runs a custom script (`call_job.sh`) on each file. Processed output folders are copied back to the host system automatically as soon as each job finishes.

---

## 📁 Folder Structure

```
pdf_processor/
├── main.py
├── file_utils.py
├── docker_utils.py
├── job_runner.py
├── DesignThought.md
├── README.md
```

---

## 🚀 Requirements

- Python 3.7+
- Docker installed and accessible
- A Docker image named `mineru:latest` that:
  - Has GPU support
  - Includes the `call_job.sh` script
- Permissions to run Docker with `--gpus=all`

---

## 🔧 Installation

1. Clone the repo:
   ```bash
   git clone <repo-url>
   cd pdf_processor
   ```

2. (Optional) Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required Python libraries (if needed for enhancement/logging):
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

To run the processor, execute:

```bash
python main.py ../example_pdfs/
```

Where `../example_pdfs/` is a directory containing PDF files. The script will:

1. Sanitize and copy PDFs to a temp folder.
2. Launch a Docker container (`mineru:latest`) with a unique name.
3. Create a temp folder inside the container and copy PDFs.
4. Run `call_job.sh` on each PDF inside the container.
5. As jobs complete, copy their output folders back to the original directory.

You’ll see real-time progress printed to the console.

---

## 📦 Example Output

```
Input path contains 5 PDF files.
Launching container: mineru_abc123...
Copying files to container...
Processing: sanitized_file_1.pdf
> call_job.sh Output: Processing page 1...
Output folder copied back to ../example_pdfs/
...
All jobs complete. Container stopped.
```

---

## 🧼 Cleanup

The script automatically removes the Docker container after execution. Temporary folders are also cleaned up.

---

## 🛠️ Customization

To customize:
- Replace `call_job.sh` in your Docker image with your own processing script.
- Modify `docker_utils.py` to mount volumes if persistent access is needed.
- Adjust filename sanitization logic in `file_utils.py`.

---

## 👨‍🔧 Maintainer

Developed by Abhinav Kumar Verma.

---

