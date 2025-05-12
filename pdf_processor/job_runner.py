import asyncio
import os
import subprocess
import shutil

async def run_single_job(container_name, container_temp_dir, filename, original_path):
    pdf_path = os.path.join(container_temp_dir, filename)
    output_path = container_temp_dir

    cmd = f"docker exec {container_name} bash -c './call_job.sh {pdf_path} {output_path}"

    print(f"[INFO] Starting job: {filename}")
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    while True:
        line = await process.stdout.readline()
        if line:
            print(f"[{filename}] {line.decode().strip()}")
        else:
            break

    await process.wait()

    folder_name = os.path.splitext(filename)[0]
    src_folder = os.path.join(container_temp_dir, folder_name)

    print(f"[INFO] Copying result folder: {folder_name} → host")

    if os.path.isfile(original_path):
        base_output_dir = os.path.dirname(original_path)
    else:
        base_output_dir = original_path

    local_result_path = os.path.join(base_output_dir, folder_name)

    cmd_cp = f"docker cp {container_name}:{src_folder} {local_result_path}"
    result = subprocess.run(cmd_cp, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"[SUCCESS] Result copied to: {local_result_path}")
    else:
        print(f"[ERROR] Failed to copy result folder for {filename}\n{result.stderr}")

def run_jobs_async(container_name, container_temp_dir, renamed_files, original_input_path):
    async def runner():
        tasks = [
            run_single_job(container_name, container_temp_dir, filename, original_input_path if os.path.isdir(original_input_path) else original_path)
            for filename, original_path in renamed_files.items()
        ]
        await asyncio.gather(*tasks)

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        print("[INTERRUPTED] Job runner interrupted by user.")
