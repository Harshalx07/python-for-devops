#!/usr/bin/env python3
"""
log_analyzer_cli.py – Day 06: CLI Tool for DevOps (argparse)

Usage:
    python log_analyzer_cli.py --file app.log
    python log_analyzer_cli.py --file app.log --out summary.txt
    python log_analyzer_cli.py --file app.log --out summary.txt --level ERROR
"""

import argparse
import os
import re
import sys
from collections import Counter
from datetime import datetime


# ──────────────────────────────────────────────
# Day 05 OOP Core (reused & extended)
# ──────────────────────────────────────────────

class LogEntry:
    """Represents a single parsed log line."""

    # Pattern: 2024-01-15 12:30:45 ERROR Some message
    PATTERN = re.compile(
        r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
        r"(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+"
        r"(?P<message>.+)"
    )

    def __init__(self, raw_line: str):
        self.raw = raw_line.strip()
        self.timestamp = None
        self.level = None
        self.message = None
        self._parse()

    def _parse(self):
        match = self.PATTERN.match(self.raw)
        if match:
            self.timestamp = match.group("timestamp")
            self.level = match.group("level")
            self.message = match.group("message")

    @property
    def is_valid(self) -> bool:
        return self.level is not None

    def __repr__(self):
        return f"<LogEntry [{self.level}] {self.message}>"


class LogAnalyzer:
    """Parses a log file and produces a summary report."""

    LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.entries: list[LogEntry] = []
        self.skipped_lines = 0

    def load(self):
        """Read and parse the log file."""
        with open(self.filepath, "r", encoding="utf-8") as fh:
            for raw_line in fh:
                if not raw_line.strip():
                    continue
                entry = LogEntry(raw_line)
                if entry.is_valid:
                    self.entries.append(entry)
                else:
                    self.skipped_lines += 1

    def filter_by_level(self, level: str) -> list[LogEntry]:
        """Return entries matching a specific log level."""
        return [e for e in self.entries if e.level == level.upper()]

    def count_by_level(self) -> Counter:
        """Count occurrences of each log level."""
        return Counter(e.level for e in self.entries)

    def generate_report(self, level_filter: str | None = None) -> str:
        """Build a human-readable summary report string."""
        lines = []
        sep = "=" * 55

        lines.append(sep)
        lines.append("         LOG ANALYSIS SUMMARY REPORT")
        lines.append(sep)
        lines.append(f"  File        : {os.path.abspath(self.filepath)}")
        lines.append(f"  Generated   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  Total lines : {len(self.entries) + self.skipped_lines}")
        lines.append(f"  Parsed      : {len(self.entries)}")
        lines.append(f"  Skipped     : {self.skipped_lines} (unrecognised format)")
        lines.append(sep)

        # Level breakdown
        counts = self.count_by_level()
        lines.append("\n  Log Level Breakdown:")
        lines.append("  " + "-" * 30)
        for lvl in self.LEVELS:
            count = counts.get(lvl, 0)
            bar = "█" * min(count, 30)
            lines.append(f"  {lvl:<10} {count:>5}  {bar}")

        # Filtered section
        if level_filter:
            lvl_up = level_filter.upper()
            filtered = self.filter_by_level(lvl_up)
            lines.append(f"\n  Filtered entries — level: {lvl_up} ({len(filtered)} found)")
            lines.append("  " + "-" * 30)
            if filtered:
                for entry in filtered:
                    lines.append(f"  [{entry.timestamp}]  {entry.message}")
            else:
                lines.append(f"  No entries found for level: {lvl_up}")

        lines.append("\n" + sep)
        return "\n".join(lines)


# ──────────────────────────────────────────────
# CLI Layer (Day 06)
# ──────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="log_analyzer_cli",
        description="🔍 DevOps Log Analyzer – parse and summarise log files from the CLI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python log_analyzer_cli.py --file app.log
  python log_analyzer_cli.py --file app.log --out summary.txt
  python log_analyzer_cli.py --file app.log --out summary.txt --level ERROR
        """,
    )

    parser.add_argument(
        "--file",
        required=True,
        metavar="PATH",
        help="Path to the log file to analyse (required)",
    )
    parser.add_argument(
        "--out",
        metavar="PATH",
        default=None,
        help="Optional path to write the summary report",
    )
    parser.add_argument(
        "--level",
        metavar="LEVEL",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        type=str.upper,
        default=None,
        help="Filter and display entries for a specific log level",
    )

    return parser


def validate_file(path: str):
    """Exit with a friendly message if the log file is not accessible."""
    if not os.path.exists(path):
        print(f"\n  ❌  Error: File not found → '{path}'")
        print("       Please check the path and try again.\n")
        sys.exit(1)
    if not os.path.isfile(path):
        print(f"\n  ❌  Error: '{path}' is not a file.\n")
        sys.exit(1)
    if os.path.getsize(path) == 0:
        print(f"\n  ⚠️   Warning: '{path}' is empty. Nothing to analyse.\n")
        sys.exit(0)


def write_output(report: str, out_path: str):
    """Write the report to an output file."""
    try:
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(report + "\n")
        print(f"\n  ✅  Report saved to: {os.path.abspath(out_path)}")
    except OSError as exc:
        print(f"\n  ❌  Could not write to '{out_path}': {exc}\n")
        sys.exit(1)


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Validate input file
    validate_file(args.file)

    # Load and analyse
    analyzer = LogAnalyzer(args.file)
    try:
        analyzer.load()
    except OSError as exc:
        print(f"\n  ❌  Failed to read file: {exc}\n")
        sys.exit(1)

    # Generate report
    report = analyzer.generate_report(level_filter=args.level)

    # Print to terminal
    print(report)

    # Write to output file if requested
    if args.out:
        write_output(report, args.out)


if __name__ == "__main__":
    main()