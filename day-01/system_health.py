# Step 1: import the library that reads system info
import psutil

# Step 2: a function that compares usage vs threshold
def check_metric(name, usage, threshold):
    if usage > threshold:
        print(f"⚠ WARNING: {name} is at {usage:.1f}% (limit: {threshold}%)")
    else:
        print(f"✓ OK: {name} is at {usage:.1f}% (limit: {threshold}%)")

# Step 3: ask the user for their thresholds
def get_thresholds():
    cpu_t = int(input("Enter CPU threshold (%): "))
    mem_t = int(input("Enter Memory threshold (%): "))
    disk_t = int(input("Enter Disk threshold (%): "))
    return cpu_t, mem_t, disk_t

# Step 4: fetch real metrics from the system
def get_metrics():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return cpu, mem, disk

# Step 5: the main function — ties everything together
def main():
    print("=== System Health Check ===")
    cpu_t, mem_t, disk_t = get_thresholds()

    print("\nChecking system metrics...")
    cpu, mem, disk = get_metrics()

    metrics = [
        ("CPU", cpu, cpu_t),
        ("Memory", mem, mem_t),
        ("Disk", disk, disk_t),
    ]

    # Step 6: loop through each metric and check it
    for name, usage, threshold in metrics:
        check_metric(name, usage, threshold)

# This ensures main() only runs when you execute the file directly
if __name__ == "__main__":
    main()
