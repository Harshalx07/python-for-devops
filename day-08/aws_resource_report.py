"""
Day 08 – AWS Automation with Python (Boto3)
Script: aws_resource_report.py

Reads EC2 instances and S3 buckets from your AWS account
and saves the output to aws_report.json
"""

import boto3
import json
from datetime import datetime


def get_ec2_instances():
    """Fetch all EC2 instances with their ID and state."""
    ec2 = boto3.client("ec2")
    response = ec2.describe_instances()

    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            # Extract Name tag if it exists
            name = "N/A"
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    name = tag["Value"]

            instances.append({
                "instance_id": instance["InstanceId"],
                "instance_type": instance["InstanceType"],
                "state": instance["State"]["Name"],
                "name": name,
                "region": boto3.session.Session().region_name,
                "launch_time": instance["LaunchTime"].isoformat(),
            })

    return instances


def get_s3_buckets():
    """Fetch all S3 buckets."""
    s3 = boto3.client("s3")
    response = s3.list_buckets()

    buckets = []
    for bucket in response.get("Buckets", []):
        buckets.append({
            "bucket_name": bucket["Name"],
            "creation_date": bucket["CreationDate"].isoformat(),
        })

    return buckets


def print_report(ec2_instances, s3_buckets):
    """Print a formatted report to the terminal."""
    print("\n" + "=" * 55)
    print("         AWS Resource Report – Boto3 (Read-Only)")
    print("=" * 55)

    # EC2
    print(f"\n📦 EC2 Instances ({len(ec2_instances)} found)")
    print("-" * 55)
    if ec2_instances:
        for inst in ec2_instances:
            state_icon = "🟢" if inst["state"] == "running" else "🔴"
            print(f"  {state_icon} {inst['instance_id']}")
            print(f"      Name  : {inst['name']}")
            print(f"      Type  : {inst['instance_type']}")
            print(f"      State : {inst['state']}")
            print(f"      Region: {inst['region']}")
            print()
    else:
        print("  No EC2 instances found.\n")

    # S3
    print(f"🪣  S3 Buckets ({len(s3_buckets)} found)")
    print("-" * 55)
    if s3_buckets:
        for bucket in s3_buckets:
            print(f"  • {bucket['bucket_name']}")
            print(f"    Created: {bucket['creation_date']}")
            print()
    else:
        print("  No S3 buckets found.\n")

    print("=" * 55)
    print("  Report saved to aws_report.json")
    print("=" * 55 + "\n")


def save_report(ec2_instances, s3_buckets, filename="aws_report.json"):
    """Save the report to a JSON file."""
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "total_ec2_instances": len(ec2_instances),
            "total_s3_buckets": len(s3_buckets),
        },
        "ec2_instances": ec2_instances,
        "s3_buckets": s3_buckets,
    }

    with open(filename, "w") as f:
        json.dump(report, f, indent=4)

    return report


def main():
    print("\n🔍 Fetching AWS resources (read-only)...\n")

    try:
        ec2_instances = get_ec2_instances()
    except Exception as e:
        print(f"⚠️  Could not fetch EC2 instances: {e}")
        ec2_instances = []

    try:
        s3_buckets = get_s3_buckets()
    except Exception as e:
        print(f"⚠️  Could not fetch S3 buckets: {e}")
        s3_buckets = []

    print_report(ec2_instances, s3_buckets)
    save_report(ec2_instances, s3_buckets)


if __name__ == "__main__":
    main()