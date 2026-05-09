"""
Day 05 – Object-Oriented Python for DevOps
Log Analyzer (OOP Refactor of Day 04)

Reads a log file, analyzes log levels (INFO / WARNING / ERROR),
and writes a summary report — all encapsulated in a class.
"""

import os
from datetime import datetime


class LogAnalyzer:
    """Analyzes a log file and produces a structured summary report."""

    def __init__(self, log_file_path: str, report_file_path: str = "summary_report.txt"):
        self.log_file_path = log_file_path
        self.report_file_path = report_file_path

        # Counters and storage – initialized here so the object always starts clean
        self.total_lines = 0
        self.counts = {"INFO": 0, "WARNING": 0, "ERROR": 0}
        self.error_lines: list[str] = []
        self.warning_lines: list[str] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Entry point: read → analyze → report."""
        print(f"[LogAnalyzer] Starting analysis on: {self.log_file_path}")
        lines = self._read_logs()
        self._analyze_logs(lines)
        self._print_summary()
        self._write_report()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _read_logs(self) -> list[str]:
        """Read the log file and return its lines. Raises FileNotFoundError if missing."""
        if not os.path.exists(self.log_file_path):
            raise FileNotFoundError(f"Log file not found: {self.log_file_path}")

        with open(self.log_file_path, "r") as f:
            lines = f.readlines()

        self.total_lines = len(lines)
        print(f"[LogAnalyzer] Read {self.total_lines} lines.")
        return lines

    def _analyze_logs(self, lines: list[str]) -> None:
        """Parse each line and update counters / capture important entries."""
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Detect log level anywhere in the line (handles varied formats)
            upper = stripped.upper()
            if " ERROR " in upper or upper.endswith("ERROR"):
                self.counts["ERROR"] += 1
                self.error_lines.append(stripped)
            elif " WARNING " in upper or upper.endswith("WARNING"):
                self.counts["WARNING"] += 1
                self.warning_lines.append(stripped)
            elif " INFO " in upper or upper.endswith("INFO"):
                self.counts["INFO"] += 1

    def _build_report_text(self) -> str:
        """Compose the full report as a string (reused by print and file write)."""
        separator = "=" * 60
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            separator,
            "           LOG ANALYSIS SUMMARY REPORT",
            separator,
            f"  Log File   : {self.log_file_path}",
            f"  Generated  : {generated_at}",
            f"  Total Lines: {self.total_lines}",
            separator,
            "  LOG LEVEL COUNTS",
            f"    INFO     : {self.counts['INFO']}",
            f"    WARNING  : {self.counts['WARNING']}",
            f"    ERROR    : {self.counts['ERROR']}",
            separator,
        ]

        if self.error_lines:
            lines.append(f"  ERROR ENTRIES ({len(self.error_lines)} found):")
            for entry in self.error_lines:
                lines.append(f"    [!] {entry}")
            lines.append(separator)

        if self.warning_lines:
            lines.append(f"  WARNING ENTRIES ({len(self.warning_lines)} found):")
            for entry in self.warning_lines:
                lines.append(f"    [~] {entry}")
            lines.append(separator)

        # Quick health verdict
        if self.counts["ERROR"] == 0 and self.counts["WARNING"] == 0:
            verdict = "✅  All clear – no errors or warnings detected."
        elif self.counts["ERROR"] == 0:
            verdict = "⚠️  No errors, but warnings need attention."
        else:
            verdict = f"❌  {self.counts['ERROR']} error(s) require immediate review."

        lines.append(f"  STATUS: {verdict}")
        lines.append(separator)

        return "\n".join(lines)

    def _print_summary(self) -> None:
        """Print the analysis report to the terminal."""
        print()
        print(self._build_report_text())

    def _write_report(self) -> None:
        """Write the analysis report to a text file."""
        with open(self.report_file_path, "w") as f:
            f.write(self._build_report_text())
            f.write("\n")
        print(f"\n[LogAnalyzer] Report saved to: {self.report_file_path}")


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

if __name__ == "__main__":
    analyzer = LogAnalyzer(
        log_file_path="sample.log",
        report_file_path="summary_report.txt",
    )
    analyzer.run()