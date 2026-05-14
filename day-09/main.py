"""
Day 09 – DevOps API with FastAPI
=================================
Endpoints:
  GET /          → Welcome message
  GET /health    → Service health status
  GET /logs      → Log analyzer (parses a local log file or generates sample data)
  GET /aws       → AWS resource summary (mocked / boto3-powered if credentials exist)
"""

import os
import re
import platform
import datetime
from collections import Counter

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

# ─────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="DevOps Toolkit API",
    description="A lightweight internal API exposing DevOps automation as HTTP endpoints.",
    version="1.0.0",
)

START_TIME = datetime.datetime.utcnow()

# ─────────────────────────────────────────────
# Helper utilities  (reused from Day-04 / Day-06 logic)
# ─────────────────────────────────────────────

SAMPLE_LOG_LINES = [
    "2024-01-15 08:01:12 INFO  Service started successfully",
    "2024-01-15 08:02:45 INFO  Connected to database",
    "2024-01-15 08:05:10 WARNING Disk usage at 75%",
    "2024-01-15 08:10:22 ERROR  Failed to connect to external API: timeout",
    "2024-01-15 08:11:00 INFO  Retrying external API connection",
    "2024-01-15 08:11:05 INFO  External API connection restored",
    "2024-01-15 08:15:33 WARNING Memory usage at 82%",
    "2024-01-15 08:20:01 ERROR  Database query timeout after 30s",
    "2024-01-15 08:21:00 CRITICAL Disk usage exceeded 90% threshold",
    "2024-01-15 08:22:10 INFO  Backup job completed",
    "2024-01-15 08:25:00 WARNING CPU spike detected: 95%",
    "2024-01-15 08:30:00 INFO  Health check passed",
    "2024-01-15 08:35:44 ERROR  Deployment rollback triggered",
    "2024-01-15 08:36:00 INFO  Rollback completed successfully",
    "2024-01-15 08:40:00 INFO  Scheduled maintenance window started",
]

LOG_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>\w+)\s+"
    r"(?P<message>.+)"
)


def parse_log_lines(lines: list[str]) -> dict:
    """Core log-analyzer logic (reused from Day-04 scripts)."""
    level_counts: Counter = Counter()
    errors = []
    warnings = []

    for line in lines:
        m = LOG_PATTERN.match(line.strip())
        if not m:
            continue
        level = m.group("level").upper()
        level_counts[level] += 1
        entry = {
            "timestamp": f"{m.group('date')} {m.group('time')}",
            "message": m.group("message"),
        }
        if level == "ERROR":
            errors.append(entry)
        elif level in ("WARNING", "WARN"):
            warnings.append(entry)

    return {
        "total_lines_parsed": len(lines),
        "level_counts": dict(level_counts),
        "errors": errors,
        "warnings": warnings,
    }


def get_aws_summary() -> dict:
    """
    AWS summary logic (reused from Day-08).
    Returns real data when boto3 + credentials are present;
    otherwise returns a clearly labelled mock response.
    """
    try:
        import boto3  # type: ignore

        ec2 = boto3.client("ec2", region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
        s3 = boto3.client("s3")

        # EC2 instances
        reservations = ec2.describe_instances()["Reservations"]
        instances = []
        for r in reservations:
            for i in r["Instances"]:
                name = next(
                    (tag["Value"] for tag in i.get("Tags", []) if tag["Key"] == "Name"),
                    "Unnamed",
                )
                instances.append(
                    {
                        "id": i["InstanceId"],
                        "name": name,
                        "type": i["InstanceType"],
                        "state": i["State"]["Name"],
                    }
                )

        # S3 buckets
        buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]

        return {
            "source": "live",
            "region": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            "ec2_instances": instances,
            "ec2_count": len(instances),
            "s3_buckets": buckets,
            "s3_count": len(buckets),
        }

    except ImportError:
        pass  # boto3 not installed
    except Exception:
        pass  # credentials not configured

    # ── Mocked fallback ──────────────────────────────────────────────────
    return {
        "source": "mock (boto3 not installed or credentials not configured)",
        "region": "us-east-1",
        "ec2_instances": [
            {"id": "i-0abc123def456789a", "name": "web-server-01",  "type": "t3.micro",  "state": "running"},
            {"id": "i-0abc123def456789b", "name": "app-server-01",  "type": "t3.small",  "state": "running"},
            {"id": "i-0abc123def456789c", "name": "db-server-01",   "type": "t3.medium", "state": "stopped"},
            {"id": "i-0abc123def456789d", "name": "bastion-host",   "type": "t2.micro",  "state": "running"},
        ],
        "ec2_count": 4,
        "s3_buckets": [
            "my-devops-artifacts-bucket",
            "my-logs-archive-bucket",
            "my-terraform-state-bucket",
        ],
        "s3_count": 3,
    }


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.get("/", tags=["General"])
def root():
    """Welcome endpoint – confirms the API is reachable."""
    return {
        "message": "👋 Welcome to the DevOps Toolkit API!",
        "docs": "/docs",
        "endpoints": ["/health", "/logs", "/aws"],
    }


@app.get("/health", tags=["General"])
def health_check():
    """
    Returns the live health status of the service.

    Includes:
    - uptime since the process started
    - host info (OS, Python version)
    - current UTC timestamp
    """
    now = datetime.datetime.utcnow()
    uptime_seconds = (now - START_TIME).total_seconds()

    return {
        "status": "healthy",
        "timestamp_utc": now.isoformat(),
        "uptime_seconds": round(uptime_seconds, 2),
        "host": {
            "os": platform.system(),
            "os_version": platform.version(),
            "python": platform.python_version(),
            "hostname": platform.node(),
        },
    }


@app.get("/logs", tags=["Log Analyzer"])
def analyze_logs(
    log_file: str = Query(
        default="",
        description="(Optional) Absolute path to a .log file on disk. "
                    "If omitted, built-in sample log data is used.",
    )
):
    """
    Analyzes log data and returns a structured summary.

    - **log_file**: path to a log file (optional). Falls back to sample data.

    Returns counts per log level, list of ERROR lines, and WARNING lines.
    """
    if log_file:
        if not os.path.isfile(log_file):
            raise HTTPException(
                status_code=404,
                detail=f"Log file not found: {log_file}",
            )
        try:
            with open(log_file, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
            source = log_file
        except OSError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    else:
        lines = SAMPLE_LOG_LINES
        source = "built-in sample data"

    summary = parse_log_lines(lines)
    return {
        "source": source,
        **summary,
    }


@app.get("/aws", tags=["AWS"])
def aws_summary():
    """
    Returns an AWS resource summary (EC2 + S3).

    Uses **boto3** when AWS credentials are configured in the environment.
    Falls back to clearly-labelled mock data otherwise — safe to demo without
    a real AWS account.

    Set environment variables to use real AWS data:
    ```
    export AWS_ACCESS_KEY_ID=...
    export AWS_SECRET_ACCESS_KEY=...
    export AWS_DEFAULT_REGION=us-east-1
    ```
    """
    return get_aws_summary()