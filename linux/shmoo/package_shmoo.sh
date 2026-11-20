#!/usr/bin/env bash
set -euo pipefail

# Ensure we are running from the 'ambarella' directory
if [[ "$(basename "$PWD")" != "ambarella" ]]; then
    echo "Error: Current directory is '$(basename "$PWD")', expected 'ambarella'." >&2
    exit 1
fi

# Check required metadata files before reading them
for meta_file in "../.soc" "../.board"; do
    if [[ ! -f "$meta_file" ]]; then
        echo "Error: Missing required file '$meta_file'." >&2
        exit 1
    fi
done

SOC="$(tr -d '[:space:]' < ../.soc)"
BOARD="$(tr -d '[:space:]' < ../.board)"

if [[ -z "$SOC" || -z "$BOARD" ]]; then
    echo "Error: .soc or .board is empty." >&2
    exit 1
fi

SOCBOARD="${SOC}_${BOARD}"
OUTPUT_PATH="out/amba_out/${SOCBOARD}/shmoo_images"
READ_DIR="${OUTPUT_PATH}/read"
WRITE_DIR="${OUTPUT_PATH}/write"
STAGING_DIR="bst_fw"
PROGRESS_OUT="Progress.txt"
ARCHIVE_NAME="bst.zip"

# Check that read/write directories and Progress.txt files exist
for dir in "$READ_DIR" "$WRITE_DIR"; do
    if [[ ! -d "$dir" ]]; then
        echo "Error: Directory not found: '$dir'" >&2
        exit 1
    fi
done

for prog_file in "${READ_DIR}/Progress.txt" "${WRITE_DIR}/Progress.txt"; do
    if [[ ! -f "$prog_file" ]]; then
        echo "Error: Missing progress file: '$prog_file'" >&2
        exit 1
    fi
done

# Verify at least one .bin file exists in both read and write directories
shopt -s nullglob
read_bins=("${READ_DIR}"/*.bin)
write_bins=("${WRITE_DIR}"/*.bin)
shopt -u nullglob

if [[ ${#read_bins[@]} -eq 0 ]]; then
    echo "Error: No .bin files found in '${READ_DIR}'." >&2
    exit 1
fi

if [[ ${#write_bins[@]} -eq 0 ]]; then
    echo "Error: No .bin files found in '${WRITE_DIR}'." >&2
    exit 1
fi

# Ensure 'zip' is available
if ! command -v zip >/dev/null 2>&1; then
    echo "Error: 'zip' command is not installed." >&2
    exit 1
fi

# Prepare staging directory and copy artifacts
mkdir -p "$STAGING_DIR"
cp "${read_bins[@]}" "${write_bins[@]}" "${STAGING_DIR}/"

cat "${READ_DIR}/Progress.txt" "${WRITE_DIR}/Progress.txt" > "$PROGRESS_OUT"

# Create zip archive
zip -r "$ARCHIVE_NAME" "$STAGING_DIR" "$PROGRESS_OUT"

echo "Successfully packaged '$ARCHIVE_NAME' for ${SOCBOARD}."
