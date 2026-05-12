"""
Day 08 – AWS CDK Demo
File: cdk-demo/cdk_demo/cdk_demo_stack.py

Defines a simple CDK stack that creates an S3 bucket.
This is Infrastructure as Code (IaC) written in Python!
"""

from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
)
from constructs import Construct


class CdkDemoStack(Stack):
    """
    A simple CDK stack that provisions one S3 bucket.

    CDK Flow:
        Python code  →  cdk synth  →  CloudFormation template  →  AWS resources
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define an S3 bucket using Python — no clicking in the AWS Console!
        demo_bucket = s3.Bucket(
            self,
            "HarshalDemoBucket",
            bucket_name="harshalx07-cdk-demo-bucket",
            versioned=True,                          # Enable versioning
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,  # No public access
            removal_policy=RemovalPolicy.DESTROY,    # Delete bucket when stack is removed
            auto_delete_objects=True,                # Auto-delete objects on removal
        )

        # Output the bucket name (visible after cdk deploy)
        from aws_cdk import CfnOutput
        CfnOutput(
            self,
            "BucketName",
            value=demo_bucket.bucket_name,
            description="The name of the S3 bucket created by CDK",
        )