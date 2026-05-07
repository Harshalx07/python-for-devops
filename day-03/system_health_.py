import psutil


def check_metric(name, usage, threshold):
    """Compare a metric's usage against its threshold and print status."""
    if usage > threshold:
        print(f"  ⚠  WARNING: {name} is at {usage:.1f}% (limit: {threshold}%)")
    else:
        print(f"  ✓  OK     : {name} is at {usage:.1f}% (limit: {threshold}%)")


def get_threshold(prompt, default):
    """
    Prompt the user for a threshold value.
    Falls back to `default` if input is empty or invalid.
    Rejects values outside 1–100.
    """
    try:
        raw = input(prompt).strip()
        if raw == "":
            print(f"    No input — using default ({default}%)")
            return default
        value = int(raw)
        if not (1 <= value <= 100):
            raise ValueError(f"{value} is out of range (1–100).")
        return value
    except ValueError as e:
        print(f"    Invalid input: {e}  Using default ({default}%).")
        return default


def get_thresholds():
    """Collect CPU, Memory, and Disk thresholds from the user."""
    print("\nSet alert thresholds (press Enter to use defaults):")
    cpu_t  = get_threshold("  CPU    threshold [default 80%]: ", default=80)
    mem_t  = get_threshold("  Memory threshold [default 80%]: ", default=80)
    disk_t = get_threshold("  Disk   threshold [default 90%]: ", default=90)
    return cpu_t, mem_t, disk_t


def get_metrics():
    """
    Read current CPU, memory, and disk usage via psutil.
    Raises RuntimeError if psutil fails to read hardware data.
    """
    try:
        cpu  = psutil.cpu_percent(interval=1)
        mem  = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return cpu, mem, disk
    except psutil.Error as e:
        raise RuntimeError(f"psutil could not read system metrics: {e}") from e


def main():
    print("=" * 45)
    print("       System Health Check — Day 03")
    print("=" * 45)

    cpu_t, mem_t, disk_t = get_thresholds()

    print("\n  Reading live system metrics...")
    try:
        cpu, mem, disk = get_metrics()
    except RuntimeError as e:
        print(f"\n  ✗  ERROR: {e}")
        print("  Cannot continue without system metrics. Exiting.")
        return  # clean exit — no crash, no traceback

    print()
    metrics = [
        ("CPU",    cpu,  cpu_t),
        ("Memory", mem,  mem_t),
        ("Disk",   disk, disk_t),
    ]

    for name, usage, threshold in metrics:
        check_metric(name, usage, threshold)

    print("\n" + "=" * 45)
    print("  Health check complete.")
    print("=" * 45)


if __name__ == "__main__":
    main()