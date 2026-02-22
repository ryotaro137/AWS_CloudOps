import os
import subprocess
import time

MAX_BATCH_SIZE_MB = 20
MAX_BATCH_SIZE_BYTES = MAX_BATCH_SIZE_MB * 1024 * 1024

def run_cmd(cmd):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing {' '.join(cmd)}:\\n{result.stderr}")
        return False
    return True

def get_modified_files():
    result = subprocess.run(['git', 'status', '-uall', '--porcelain'], capture_output=True, text=True)
    files = []
    for line in result.stdout.splitlines():
        if line.strip():
            # e.g. " M path/to/file" or "?? path/to/file"
            file_path = line[3:]
            # handle quotes if any
            if file_path.startswith('"') and file_path.endswith('"'):
                file_path = file_path[1:-1]
            if os.path.exists(file_path):
                files.append(file_path)
    return files

def main():
    # Make sure we are on tracked branches or something
    # let's initial commit if branch has no commits
    
    files = get_modified_files()
    if not files:
        print("No files to commit.")
        return

    batches = []
    current_batch = []
    current_size = 0

    for f in files:
        if os.path.isfile(f):
            size = os.path.getsize(f)
            if size > 100 * 1024 * 1024:
                print(f"WARNING: {f} is larger than 100MB, GitHub might reject it.")
            
            if current_size + size > MAX_BATCH_SIZE_BYTES and current_batch:
                batches.append(current_batch)
                current_batch = []
                current_size = 0
            
            current_batch.append(f)
            current_size += size
        else:
            # directory or something, add as small size
            current_batch.append(f)
            
    if current_batch:
        batches.append(current_batch)

    print(f"Total files: {len(files)}, split into {len(batches)} batches.")

    batch_num = 1
    for batch in batches:
        print(f"\\n--- Processing Batch {batch_num}/{len(batches)} ---")
        for f in batch:
            if run_cmd(['git', 'add', f]) == False:
                print("Failed to add file, continuing...")
        
        commit_msg = f"Batch commit {batch_num}/{len(batches)}"
        if run_cmd(['git', 'commit', '-m', commit_msg]):
            print("Commit successful. Pushing to origin main...")
            retries = 3
            while retries > 0:
                if run_cmd(['git', 'push', 'origin', 'main']):
                    break
                print("Push failed. Retrying...")
                retries -= 1
                time.sleep(3)
        
        batch_num += 1

if __name__ == "__main__":
    main()
