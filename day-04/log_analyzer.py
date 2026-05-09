"""
log_analyzer.py - Day 04: File Handling & Log Analysis for DevOps
Reads a log file and counts INFO, WARNING, and ERROR messages.
"""

import json
from datetime import datetime


def read_log_file(filepath):
    """Read and return lines from a log file."""
    with open(filepath, "r") as f:
        lines = f.readlines()
    if not lines:
        raise ValueError(f"Log file '{filepath}' is empty.")
    return lines


def analyze_logs(lines):
    """Parse log lines and count occurrences of each log level."""
    counts = {"INFO": 0, "WARNING": 0, "ERROR": 0}
    details = {"INFO": [], "WARNING": [], "ERROR": []}

    for line in lines:
        line = line.strip()
        if not line:
            continue
        for level in counts:
            if level in line:
                counts[level] += 1
                details[level].append(line)
                break  # avoid double-counting

    return counts, details


def print_summary(counts, total):
    """Print a formatted summary to the terminal."""
    print("\n" + "=" * 45)
    print("         LOG ANALYSIS SUMMARY")
    print("=" * 45)
    print(f"  Total log lines analyzed : {total}")
    print(f"  INFO     : {counts['INFO']}")
    print(f"  WARNING  : {counts['WARNING']}")
    print(f"  ERROR    : {counts['ERROR']}")
    print("=" * 45 + "\n")


def write_summary(counts, details, total, output_path):
    """Write the summary as a JSON file."""
    summary = {
        "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_lines": total,
        "counts": counts,
        "details": details,
    }
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=4)
    print(f"Summary written to: {output_path}")


def main():
    log_file = "app.log"
    output_file = "log_summary.json"

    try:
        lines = read_log_file(log_file)
        counts, details = analyze_logs(lines)
        total = len([l for l in lines if l.strip()])
        print_summary(counts, total)
        write_summary(counts, details, total, output_file)

    except FileNotFoundError:
        print(f"ERROR: File '{log_file}' not found. Please check the path.")
    except ValueError as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()