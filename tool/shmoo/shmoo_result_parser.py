import os
import re
import sys
from openpyxl import Workbook

ROOT_DIR = "./logs"

def extract_column_name(filename):
    """
    Extract OOOO from filename like:
        xxx_OOOO.log
    """
    match = re.search(r'_(.+?)(?:\.|$)', filename)
    if match:
        return match.group(1)
    return filename


def parse_boundary(filepath, mode):

    if mode == "read":
        pattern =  r'rdq offset boundary is\s*(\[[^\]]+\])'
    else:
        pattern = r'wdq offset boundary is\s*(\[[^\]]+\])'
    
    results = []
    
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:

            content = f.read()

            matches = re.findall(pattern,
                                 content,
                                 re.IGNORECASE)
            results.extend(matches)

    except Exception as e:
        print(f"Read fail {filepath}: {e}")

    return  " ".join(results)
    
    
def collect_data(mode):
    """
    mode = read / write
    """
    result = {}
    all_columns = set()

    for hostname in os.listdir(ROOT_DIR):

        host_path = os.path.join(ROOT_DIR, hostname)

        if not os.path.isdir(host_path):
            continue

        mode_path = os.path.join(host_path, mode)

        if not os.path.isdir(mode_path):
            continue

        for level in ["high", "low"]:

            level_path = os.path.join(mode_path, level)

            if not os.path.isdir(level_path):
                continue

            row_name = f"{hostname}_{level}"

            result[row_name] = {}

            for logfile in os.listdir(level_path):

                log_path = os.path.join(level_path, logfile)

                if not os.path.isfile(log_path):
                    continue

                column_name = extract_column_name(logfile)
                boundary = parse_boundary(log_path, mode)
                all_columns.add(column_name)

                result[row_name][column_name] = boundary

    return result, sorted(all_columns)

def generate_xlsx(mode):

    data, columns = collect_data(mode)

    wb = Workbook()
    ws = wb.active

    ws.title = f"{mode}_result"

    #
    # Header
    #
    ws.cell(row=1, column=1, value="ID ({})".format(mode))

    for col_idx, col_name in enumerate(columns, start=2):
        ws.cell(row=1, column=col_idx, value=col_name)

    #
    # Content
    #
    row_idx = 2

    for row_name, row_data in data.items():

        ws.cell(row=row_idx, column=1, value=row_name)

        for col_idx, col_name in enumerate(columns, start=2):

            if col_name in row_data:
                ws.cell(row=row_idx, column=col_idx,
                        value=row_data[col_name])

        row_idx += 1

    output_name = f"{mode}_result.xlsx"

    wb.save(output_name)

    print(f"Generate {output_name}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ROOT_DIR=sys.argv[1]
    generate_xlsx("read")
    generate_xlsx("write")