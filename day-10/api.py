#!/usr/bin/env python3
"""
api.py
------
FastAPI wrapper around the log_analyzer module.

Exposes two endpoints:
  POST /analyze  — upload or pass a log file path, get back a JSON summary
  GET  /health   — simple health check

Run with:
    uvicorn api:app --reload --port 8000

Then hit:
    curl -X POST http://localhost:8000/analyze \
         -H "Content-Type: application/json" \
         -d '{"filepath": "logs/app.log", "level": "ERROR"}'
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Import our core log analysis logic
from log_analyzer import parse_log_file, analyze_logs

# ──────────────────────────────────────────────
# App setup
# ──────────────────────────────────────────────

app = FastAPI(
    title="DevOps Log Analyzer API",
    description="Analyze log files and get structured summaries via REST API",
    version="1.0.0",
)


# ──────────────────────────────────────────────
# Request / Response schemas
# ──────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    filepath: str                   # Path to the log file on the server
    level: Optional[str] = None     # Optional: filter by level (ERROR / WARNING / INFO)

    class Config:
        json_schema_extra = {
            "example": {
                "filepath": "logs/app.log",
                "level": "ERROR",
            }
        }


class LevelCount(BaseModel):
    level: str
    count: int


class AnalyzeResponse(BaseModel):
    total_lines: int
    level_counts: dict
    filtered_level: str
    filtered_entries: list
    generated_at: str


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Simple liveness check — used by load balancers / monitoring tools."""
    return {"status": "ok", "service": "log-analyzer-api"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_log(request: AnalyzeRequest):
    """
    Parse a log file and return a structured summary.

    - **filepath**: path to the log file (relative to where the server runs)
    - **level**: optional log level filter (INFO / WARNING / ERROR)
    """
    try:
        entries = parse_log_file(request.filepath)
    except SystemExit:
        # parse_log_file calls sys.exit on missing file; convert to HTTP error
        raise HTTPException(status_code=404, detail=f"File not found: {request.filepath}")

    summary = analyze_logs(entries, filter_level=request.level)
    return summary


# ──────────────────────────────────────────────
# Dev server entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)