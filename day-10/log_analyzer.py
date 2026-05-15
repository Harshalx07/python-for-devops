#!/usr/bin/env python3
"""
log_analyzer.py
---------------
DevOps Capstone Project - Log Analysis Tool

Parses log files, counts severity levels, extracts errors/warnings,
and generates a summary report. Supports CLI arguments and can export
results as JSON for downstream use (e.g., FastAPI wrapper).

Usage:
    python log_analyzer.py --file logs/app.log
    python log_analyzer.py --file logs/app.log --level ERROR
    python log_analyzer.py --file logs/app.log --export report.json
"""

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


# ──────────────────────────────────────────────
# Core parsing logic
# ──────────────────────────────────────────────

def parse_log_file(filepath: str) -> list[dict]:
    """
    Read a log file and return a list of parsed log entries.

    Each entry is a dict with keys: timestamp, level, message.
    Lines that don't match the expected format are skipped with a warning.
    """
    entries = []
    path = Path(filepath)

    if not path.exists():
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)

    with open(path, "r") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            # Expected format: YYYY-MM-DD HH:MM:SS LEVEL message
            parts = line.split(maxsplit=3)
            if len(parts) < 4:
                print(f"[WARN] Skipping malformed line {line_num}: {line[:60]}")
                continue

            date_str, time_str, level, message = parts
            entries.append({
                "timestamp": f"{date_str} {time_str}",
                "level": level.strip(),
                "message": message.strip(),
                "raw": line,
            })

    return entries


def analyze_logs(entries: list[dict], filter_level: str = None) -> dict:
    """
    Analyse parsed log entries and return a summary dict.

    Args:
        entries: list of parsed log dicts
        filter_level: if set (e.g. "ERROR"), only include that level in details

    Returns:
        A summary dict with counts, filtered entries, and metadata.
    """
    level_counts = Counter(e["level"] for e in entries)

    # Apply level filter for the detailed listing
    if filter_level:
        filtered = [e for e in entries if e["level"] == filter_level.upper()]
    else:
        # Default: show ERROR and WARNING entries
        filtered = [e for e in entries if e["level"] in ("ERROR", "WARNING")]

    return {
        "total_lines": len(entries),
        "level_counts": dict(level_counts),
        "filtered_level": filter_level or "ERROR + WARNING",
        "filtered_entries": filtered,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ──────────────────────────────────────────────
# Output / reporting helpers
# ──────────────────────────────────────────────

def print_report(summary: dict) -> None:
    """Print a human-readable summary to stdout."""
    print("\n" + "=" * 55)
    print("       DevOps Log Analyzer — Summary Report")
    print("=" * 55)
    print(f"  Generated : {summary['generated_at']}")
    print(f"  Total lines parsed : {summary['total_lines']}")
    print()

    print("  Log Level Breakdown:")
    for level, count in sorted(summary["level_counts"].items()):
        bar = "█" * count
        print(f"    {level:<10} {count:>3}  {bar}")

    print()
    print(f"  Showing entries — filter: [{summary['filtered_level']}]")
    print("-" * 55)

    if not summary["filtered_entries"]:
        print("  No matching entries found.")
    else:
        for entry in summary["filtered_entries"]:
            print(f"  [{entry['level']:<8}] {entry['timestamp']}  {entry['message']}")

    print("=" * 55 + "\n")


def export_json(summary: dict, output_path: str) -> None:
    """Write the summary dict to a JSON file."""
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[INFO] Report exported to: {output_path}")


# ──────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────

def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DevOps Log Analyzer — parse and summarise log files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python log_analyzer.py --file logs/app.log
  python log_analyzer.py --file logs/app.log --level ERROR
  python log_analyzer.py --file logs/app.log --export report.json
        """,
    )
    parser.add_argument("--file", required=True, help="Path to the log file")
    parser.add_argument(
        "--level",
        default=None,
        help="Filter output to a specific log level (INFO / WARNING / ERROR)",
    )
    parser.add_argument(
        "--export",
        default=None,
        metavar="OUTPUT.json",
        help="Export the summary to a JSON file",
    )
    return parser


def main():
    parser = build_cli()
    args = parser.parse_args()

    # 1. Parse
    entries = parse_log_file(args.file)
    print(f"[INFO] Parsed {len(entries)} log entries from '{args.file}'")

    # 2. Analyse
    summary = analyze_logs(entries, filter_level=args.level)

    # 3. Report
    print_report(summary)

    # 4. Optional JSON export
    if args.export:
        export_json(summary, args.export)


if __name__ == "__main__":
    main()