#!/usr/bin/env bash

# Get the directory where this shell script is located
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=================================================="
echo "Scanning for Makefiles starting from: $BASE_DIR"
echo "=================================================="

# Find all Makefiles recursively and process their parent directories
find "$BASE_DIR" -name "Makefile" -type f | while read -r makefile_path; do
    target_dir="$(dirname "$makefile_path")"
    
    echo ""
    echo "--------------------------------------------------"
    echo "[*] Found Makefile in: $target_dir"
    echo "[*] Executing 'make all'..."
    echo "--------------------------------------------------"
    
    # Run 'make all' inside a subshell so directory changes don't affect the loop
    (
        cd "$target_dir" || exit 1
        if make clean; then
            echo "[+] Successfully completed 'make all' in: $target_dir"
        else
            echo "[-] ERROR: 'make all' failed in: $target_dir" >&2
            exit 1
        fi
    )
    
    # Optional: uncomment the line below if you want the script to stop 
    # immediately upon the first failure of any 'make all' command.
    # [ $? -ne 0 ] && exit 1
done

echo ""
echo "=================================================="
echo "All directories processed."
echo "=================================================="