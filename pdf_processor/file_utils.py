import os
import shutil
import re

def sanitize_filename(filename):
    name, ext = os.path.splitext(filename)
    safe_name = re.sub(r'[^\w\.]', '_', name)
    return f"{safe_name}{ext}"

def prepare_pdf_files(input_path, destination_folder):
    renamed_files = {}

    if os.path.isfile(input_path) and input_path.lower().endswith(".pdf"):
        files_to_copy = [input_path]
    elif os.path.isdir(input_path):
        files_to_copy = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(input_path, f))
        ]
    else:
        print("[WARN] Input is neither a PDF file nor a valid folder.")
        return renamed_files

    for filepath in files_to_copy:
        original_name = os.path.basename(filepath)
        sanitized_name = sanitize_filename(original_name)
        destination_path = os.path.join(destination_folder, sanitized_name)

        shutil.copy2(filepath, destination_path)
        renamed_files[sanitized_name] = destination_path  # Store the full destination path

        print(f"[INFO] Copied and sanitized: {original_name} → {sanitized_name}")

    return renamed_files


def get_output_folder_name(pdf_filename: str) -> str:
    """
    Derives the output folder name from a PDF filename.
    Assumes the folder name is the filename without the '.pdf' extension.
    """
    return os.path.splitext(pdf_filename)[0]

