import csv
import sys
from datetime import datetime


def parse_file_line(line):
    # strip leading tabs first
    stripped = line.lstrip("\t")
    indent = len(line) - len(stripped)
    s = stripped.rstrip("\n\r")
    if s.startswith(("D", "F")):
        t = s[0]
        size_part, ts_part = s[1:].split(".", 1)
        size = int(size_part)
        ts = int(ts_part)
        # Handle invalid timestamps (e.g., -1)
        if ts < 0:
            dt = "1970-01-01T00:00:00"
        else:
            # FAT timestamp decoding (dosdate)
            dos_time = ts & 0xFFFF
            dos_date = ts >> 16

            sec = (dos_time & 0x1F) * 2
            minute = (dos_time >> 5) & 0x3F
            hour = dos_time >> 11

            day = dos_date & 0x1F
            month = (dos_date >> 5) & 0xF
            year = (dos_date >> 9) + 1980

            try:
                dt = datetime(year, month, day, hour, minute, sec).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
            except ValueError:
                dt = "1970-01-01T00:00:00"  # Invalid date
        return {"indent": indent, "type": t, "size": size, "ts": ts, "ts_str": dt}
    else:
        raise ValueError("not D/F line")


def parse_name_line(line):
    stripped = line.lstrip("\t")
    indent = len(line) - len(stripped)
    name = stripped.rstrip("\n\r")
    return {"indent": indent, "name": name}


def match_and_dump(input_path, out_path):
    recs = []
    input_path = input_path.rstrip('.IDX').rstrip('.FILE')
    idx_path, file_path = input_path + ".IDX", input_path + ".FILE"

    with open(file_path, "r", encoding="utf-16", errors="replace") as f:
        file_lines = f.readlines()
    with open(idx_path, "r", encoding="utf-16", errors="replace") as f:
        idx_lines = f.readlines()

    # Filter out empty lines
    file_lines = [line for line in file_lines if line.strip()]
    idx_lines = [line for line in idx_lines if line.strip()]

    assert len(file_lines) == len(idx_lines), "line count mismatch"

    for i in range(len(idx_lines)):
        fld = parse_file_line(file_lines[i])
        named = parse_name_line(idx_lines[i])
        assert fld["indent"] == named["indent"], f"indent mismatch at line {i}"
        recs.append(
            {
                "depth": named["indent"],
                "name": named["name"],
                "is_dir": (fld["type"] == "D"),
                "size_bytes": fld["size"],
                "mtime_ts": fld["ts"],
                "mtime_str": fld["ts_str"],
            }
        )

    # Optional: walk the tree and print as CSV
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["FullPath", "IsDir", "SizeBytes", "MtimeStr"])
        stack = []  # path components
        for r in recs:
            depth = r["depth"]
            while len(stack) > depth:
                stack.pop()
            stack.append(r["name"])
            path = "/".join(stack)
            is_dir = "1" if r["is_dir"] else "0"
            writer.writerow([path, is_dir, r["size_bytes"], r["mtime_str"]])


def main():
    if len(sys.argv) != 3:
        print("Usage: python decode_cdindex.py <input_file> <output_csv>")
        sys.exit(1)
    input_path = sys.argv[1]
    out_path = sys.argv[2]
    match_and_dump(input_path, out_path)


if __name__ == "__main__":
    main()
