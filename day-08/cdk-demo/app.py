"""
Day 08 – AWS CDK Demo
File: cdk-demo/app.py

This is the CDK app entry point.
Run `cdk synth` to generate the CloudFormation template.
Run `cdk deploy` to actually create the resources in AWS.
"""

import aws_cdk as cdk
from cdk_demo.cdk_demo_stack import CdkDemoStack

app = cdk.App()

CdkDemoStack(
    app,
    "CdkDemoStack",
    env=cdk.Environment(
        account="YOUR_AWS_ACCOUNT_ID",   # Replace with your Account ID
        region="ap-south-1",             # Mumbai region
    ),
    description="Day 08 – Harshal CDK Demo Stack",
)

app.synth()