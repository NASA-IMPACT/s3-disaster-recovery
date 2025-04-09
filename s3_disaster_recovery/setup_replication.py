# setup_replication.py
from aws_cdk import (
    aws_s3 as s3,
    aws_iam as iam,
    custom_resources as cr
)
import aws_cdk as cdk
from constructs import Construct


class SetUpReplication(Construct):
    def __init__(self, scope: Construct, id: str, source_bucket: s3.Bucket, destination_bucket: s3.Bucket, source_bucket_name: str, destination_bucket_name: str, bucket_hash: str,  permissions_boundary_arn: str):
        super().__init__(scope, id)
        # Create IAM role for S3 Replication
        replication_iam_role = iam.Role(
            self,
            f"S3ReplicationRole-{bucket_hash}",
            assumed_by=iam.ServicePrincipal("s3.amazonaws.com"),
            permissions_boundary=iam.ManagedPolicy.from_managed_policy_arn(
                    self, "PermissionsBoundary", permissions_boundary_arn
                ) #if permissions_boundary_arn else None            
        )

        # Add permissions for source bucket replication
        replication_iam_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "s3:GetReplicationConfiguration",
                "s3:ListBucket",
                "s3:GetBucketVersioning",
                "s3:GetBucketLocation",
                "s3:GetObjectVersionForReplication",
                "s3:GetObjectVersionAcl",
                "s3:GetObjectVersionTagging",
                "s3:InitiateReplication",
                "s3:GetReplicationConfiguration",
                "s3:PutInventoryConfiguration",
                "s3:GetBucketInventoryConfiguration",
                "s3:CreateJob",
                "s3:PutJobTagging",
                "s3control:CreateJob",
                "s3control:PutJobTagging"

            ],
            resources=[source_bucket.bucket_arn, f"{source_bucket.bucket_arn}/*"]
        ))

        # Add permissions to write to the destination bucket
        replication_iam_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:ReplicateObject",
                "s3:ReplicateDelete",
                "s3:ReplicateTags",
                "s3:GetObjectVersionTagging"],
            resources=[f"{destination_bucket.bucket_arn}/*"]
        ))
        replication_iam_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "s3:GetBucketVersioning",
                "s3:GetBucketLocation"
            ],
            resources=[destination_bucket.bucket_arn]
        ))

        # Custom Resource to apply S3 Replication Configuration
        custom_resource = cr.AwsCustomResource(
            self, 
            f"S3ReplicationCustomResource-{bucket_hash}",
            on_create=cr.AwsSdkCall(
                service="S3",
                action="putBucketReplication",
                parameters={
                    "Bucket": source_bucket_name,
                    "ReplicationConfiguration": {
                        "Role": replication_iam_role.role_arn,
                        "Rules": [
                            {
                                "ID": f"FullBucketReplication-{bucket_hash}",
                                "Status": "Enabled",
                                "Priority": 0,
                                "DeleteMarkerReplication": {"Status": "Disabled"},
                                "Filter": {},
                                "Destination": {
                                    "Bucket": f"arn:aws:s3:::{destination_bucket_name}",
                                    "StorageClass": "STANDARD"
                                }
                            }
                        ]
                    }
                },
                physical_resource_id=cr.PhysicalResourceId.of(f"S3ReplicationConfig-{bucket_hash}")
            ),
            on_delete=cr.AwsSdkCall(
                service="S3",
                action="deleteBucketReplication",
                parameters={
                    "Bucket": source_bucket_name
                },
                physical_resource_id=cr.PhysicalResourceId.of(f"S3ReplicationConfig-{bucket_hash}")
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=["s3:PutReplicationConfiguration","s3:DeleteReplicationConfiguration"],
                    resources=[source_bucket.bucket_arn]
                ),
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    resources=[replication_iam_role.role_arn]
                ),
                iam.PolicyStatement(
                    actions=["iam:PassRole","iam:CreateRole","iam:TagRole"],
                    resources=[replication_iam_role.role_arn]  
                )
            ]),

        )

