# add_lifecycle_rule.py
from aws_cdk import (
    aws_s3 as s3,
    aws_iam as iam,
    custom_resources as cr
)
import aws_cdk as cdk
from constructs import Construct


class AddLifeCycleRule(Construct):
    def __init__(self, scope: Construct, id: str, destination_bucket_name: str, bucket_hash: str, permissions_boundary_arn: str):
        super().__init__(scope, id)
        # Create an IAM role for the custom resource to assume
        lifecycle_role = iam.Role(
            self, 
            f"LifecycleManagementRole-{bucket_hash}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            permissions_boundary=iam.ManagedPolicy.from_managed_policy_arn(
                    self, "PermissionsBoundaryLC", permissions_boundary_arn
                ) if permissions_boundary_arn else None
        )     

        # Attach permissions to the role
        lifecycle_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:PutBucketLifecycleConfiguration"],
            resources=[f"arn:aws:s3:::{destination_bucket_name}"]
        ))

        # Create a custom role for AWS Lambda used by the custom resource with a permissions boundary
        custom_resource_role = iam.Role(
            self,
            f"CustomResourceLambdaExecutionRoleLC-{bucket_hash}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            permissions_boundary=iam.ManagedPolicy.from_managed_policy_arn(
                self, f"CustomPermissionsBoundaryLC-{bucket_hash}", permissions_boundary_arn
            ) if permissions_boundary_arn else None
        )

        # Grant the custom resource role permissions
        custom_resource_role.add_to_policy(iam.PolicyStatement(
            actions=["sts:AssumeRole"],
            resources=[lifecycle_role.role_arn]
        ))

        # Create the custom resource to manage the lifecycle configuration
        custom_resource = cr.AwsCustomResource(
            self,
            f"S3LifecycleCustomResource-{bucket_hash}",
            on_create=cr.AwsSdkCall(
                service="S3",
                action="putBucketLifecycleConfiguration",
                parameters={
                    "Bucket": destination_bucket_name,
                    "LifecycleConfiguration":{
                            'Rules': [
                                {
                                    'ID': f'RecoveryBucketRule-{bucket_hash}',
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
                physical_resource_id=cr.PhysicalResourceId.of(f"S3LifecycleConfiguration-{bucket_hash}")
            ),
            on_delete=cr.AwsSdkCall(
            service="S3",
            action="deleteBucketLifecycle",
            parameters={"Bucket": destination_bucket_name},
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=["s3:PutBucketLifecycleConfiguration","s3:PutLifecycleConfiguration","s3:DeleteBucketLifecycle"],
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
            ]),
            role=custom_resource_role
        )

