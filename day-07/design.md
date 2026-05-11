# Day 07 – Design Document: Log File Analyzer Script

## Which Script Am I Planning?

**Script chosen:** Log File Analyzer (from Day 05)  
**File:** `log_analyzer.py`  
**Purpose:** Scan a server log file and report errors, warnings, and suspicious activity.

---

## What Problem Am I Solving?

- In DevOps, servers generate huge log files every day
- Manually reading thousands of log lines is slow and error-prone
- Engineers need to quickly find: ERROR lines, WARNING lines, and failed login attempts
- This script automates that process so any team member can run it in seconds

---

## What Input Does My Script Need?

- A log file path (example: `/var/log/app.log` or `server.log`)
- The file should be a plain text file with one log entry per line
- Each line typically looks like:

```
2025-01-10 14:32:01 ERROR Database connection failed
2025-01-10 14:33:45 WARNING Disk usage above 80%
2025-01-10 14:35:10 INFO User login successful
```

**Input summary:**
- `log_file` → path to the log file (string)
- User provides this as a command-line argument or hardcoded path

---

## What Output Should My Script Give?

The script should print a clean summary to the terminal:

```
=== Log File Analysis Report ===
Total lines scanned : 1500
ERROR count         : 23
WARNING count       : 47
INFO count          : 1430

Top 5 ERROR messages:
  - Database connection failed (x8)
  - Timeout on API call (x6)
  - Null pointer exception (x5)
  - Disk read error (x3)
  - Auth token expired (x1)

Report saved to: log_report.txt
```

**Output summary:**
- Total line count
- Count of each log level (ERROR, WARNING, INFO)
- Top repeated error messages
- A saved `.txt` report file

---

## What Are the Main Steps?

1. **Accept input** → Get the log file path from the user (command-line argument)
2. **Open the file** → Read the file line by line
3. **Parse each line** → Check if the line contains ERROR, WARNING, or INFO
4. **Count and collect** → Keep a counter for each level; store ERROR messages in a list
5. **Find top errors** → Group duplicate error messages and count occurrences
6. **Display results** → Print the summary to the terminal in a readable format
7. **Save report** → Write the same summary to a `log_report.txt` file
8. **Handle errors** → If the file doesn't exist, show a friendly message instead of crashing

---

## Edge Cases to Think About

- What if the log file is empty? → Print "No log entries found"
- What if the file path is wrong? → Print "File not found: <path>"
- What if a line has no log level keyword? → Skip it or count as UNKNOWN
- What if the file is very large (1 GB+)? → Read line by line, not all at once (memory safe)

---

## Why This Script Matters in DevOps

| Without Script | With Script |
|---|---|
| Engineer reads 5000 lines manually | Script reads in 2 seconds |
| Easy to miss errors | Every ERROR is captured |
| No record of past issues | Report file saved for audit |
| Inconsistent checks | Same result every time (automation) |

---

## Tools / Libraries Needed

- `sys` → to accept command-line arguments
- `os` → to check if file exists
- `collections.Counter` → to count top repeated errors
- No external libraries needed (pure Python)

---

## Summary (One Line)

> **Script lega ek log file, dhundega errors aur warnings, aur ek clean report dega — terminal pe bhi, file mein bhi.**

---

*Day 07 | Python for DevOps | TrainWithShubham*