import os
import subprocess
import hashlib
import json
import time

max_retries = 3

bucket_binding = "samsara-super-zoom"
local_tile_root = "tiles"
wrangler_path = r"C:\Users\brian\AppData\Roaming\npm\wrangler.cmd"
hash_cache_file = ".tile_hashes.json"

# Load or initialize the hash cache
if os.path.exists(hash_cache_file):
    with open(hash_cache_file, "r") as f:
        hash_cache = json.load(f)
else:
    hash_cache = {}

def compute_file_hash(filepath):
    """Compute SHA256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def save_hash_cache():
    with open(hash_cache_file, "w") as f:
        json.dump(hash_cache, f, indent=2)

for root, dirs, files in os.walk(local_tile_root):
    for file in files:
        if not file.lower().endswith(".png"):
            continue

        local_path = os.path.join(root, file)
        relative_path = os.path.relpath(local_path, local_tile_root).replace("\\", "/")
        remote_path = f"tiles/{relative_path}"

        # Compute hash and compare
        file_hash = compute_file_hash(local_path)
        if remote_path in hash_cache and hash_cache[remote_path] == file_hash:
            print(f"✅ Skipping unchanged: {remote_path}")
            continue

        print(f"⬆️ Uploading {remote_path}...")

        for attempt in range(1, max_retries + 1):
            try:
                result = subprocess.run(
                    [
                        wrangler_path,
                        "r2", "object", "put",
                        f"{bucket_binding}/{remote_path}",
                        "--file", local_path,
                        "--config", "wrangler.toml",
                        "--remote"
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )

                if result.returncode == 0:
                    print(f"✅ Uploaded: {remote_path}")
                    hash_cache[remote_path] = file_hash
                    save_hash_cache()
                    break  # success
                else:
                    print(f"❌ Failed attempt {attempt} for {remote_path}")
                    print(f"Stderr: {result.stderr}")
                    if attempt < max_retries:
                        time.sleep(1.5 * attempt)
                    else:
                        print(f"💥 Giving up after {max_retries} attempts.")
            except Exception as e:
                print(f"💥 Error uploading {remote_path}: {str(e)}")
