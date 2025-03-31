# add_lifecycle_rule.py
from aws_cdk import (
    aws_s3 as s3,
    aws_iam as iam,
    custom_resources as cr
)
import aws_cdk as cdk
from constructs import Construct


class AddLifeCycleRule(Construct):
    def __init__(self, scope: Construct, id: str, destination_bucket_name: str):
        super().__init__(scope, id)
        # Create an IAM role for the custom resource to assume
        lifecycle_role = iam.Role(
            self, "LifecycleManagementRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        # Attach permissions to the role
        lifecycle_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:PutBucketLifecycleConfiguration"],
            resources=[f"arn:aws:s3:::{destination_bucket_name}"]
        ))

        # Create the custom resource to manage the lifecycle configuration
        custom_resource = cr.AwsCustomResource(
            self,
            "S3LifecycleCustomResource",
            on_create=cr.AwsSdkCall(
                service="S3",
                action="putBucketLifecycleConfiguration",
                parameters={
                    "Bucket": destination_bucket_name,
                    "LifecycleConfiguration":{
                            'Rules': [
                                {
                                    'ID': 'RecoveryBucketRule',
                                    'Status': 'Enabled',
                                    "Prefix": "",
                                    'Transitions': [
                                        {
                                            'Days': 30,
                                            'StorageClass': 'STANDARD_IA'
                                        },
                                        {
                                            'Days': 60,
                                            'StorageClass': 'GLACIER'
                                        },
                                        {
                                            'Days': 180,
                                            'StorageClass': 'DEEP_ARCHIVE'
                                        },
                                    ]
                                },
                            ]
                        },
                },
                physical_resource_id=cr.PhysicalResourceId.of("S3LifecycleConfiguration")
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=["s3:PutBucketLifecycleConfiguration","s3:PutLifecycleConfiguration"],
                    resources=[f"arn:aws:s3:::{destination_bucket_name}"]
                ),
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    resources=[lifecycle_role.role_arn]
                ),
                iam.PolicyStatement(
                    actions=["iam:PassRole"],
                    resources=[lifecycle_role.role_arn]
                ),
            ])
        )
