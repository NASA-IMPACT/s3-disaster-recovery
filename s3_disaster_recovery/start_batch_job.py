
# start_batch_job.py
from aws_cdk import (
    aws_s3 as s3,
    aws_iam as iam,
    custom_resources as cr
)
import aws_cdk as cdk
from constructs import Construct


class StartBatchJob(Construct):
    def __init__(self, scope: Construct, id: str, source_bucket: s3.Bucket, destination_bucket: s3.Bucket, source_bucket_name: str, destination_bucket_name: str, bucket_hash: str,  permissions_boundary_arn: str):
        super().__init__(scope, id)

        # IAM role for batch operations
        batch_operations_role = iam.Role(
            self,
            f"BatchOperationsRole-{bucket_hash}",
            assumed_by=iam.ServicePrincipal("batchoperations.s3.amazonaws.com"),
            permissions_boundary=iam.ManagedPolicy.from_managed_policy_arn(
                    self, "PermissionsBoundaryBatch", permissions_boundary_arn
                ) if permissions_boundary_arn else None
        )

        # Grant permissions to access buckets
        batch_operations_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:GetBucketLocation",
                "s3:ListBucket",
                "s3:GetBucketVersioning",
                "s3:GetReplicationConfiguration"
            ],
            resources=[
                source_bucket.bucket_arn,
                f"{source_bucket.bucket_arn}/*"
            ]
        ))
        batch_operations_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "s3:ReplicateObject",
                "s3:ReplicateDelete",
                "s3:ReplicateTags",
                "s3:GetObjectVersionTagging"
            ],
            resources=[
                destination_bucket.bucket_arn,
                f"{destination_bucket.bucket_arn}/*"
            ]
        ))
        batch_operations_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:GetBucketVersioning",
                "s3:GetBucketLocation"],
            resources=[destination_bucket.bucket_arn]
        ))
        batch_operations_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:GetReplicationConfiguration",
                "s3:ListBucket",
                "s3:PutObject",
                "s3:GetBucketVersioning",
                "s3:GetBucketLocation",
                "s3:GetObjectVersionForReplication",
                "s3:GetObjectVersionAcl",
                "s3:GetObjectVersionTagging",
                "s3:InitiateReplication",
                "s3:GetReplicationConfiguration",
                "s3:PutInventoryConfiguration"
            ],
            resources=[source_bucket.bucket_arn, f"{source_bucket.bucket_arn}/*"]
        ))

        # Allowing the role to create job
        batch_operations_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:CreateJob"],
            resources=["*"]
        ))


        # Create a custom role for AWS Lambda used by the custom resource with a permissions boundary
        custom_resource_role = iam.Role(
            self,
            f"CustomResourceLambdaExecutionRoleBatch-{bucket_hash}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            permissions_boundary=iam.ManagedPolicy.from_managed_policy_arn(
                self, f"CustomPermissionsBoundaryBatch-{bucket_hash}", permissions_boundary_arn
            ) if permissions_boundary_arn else None
        )

        # Grant the custom resource role permissions
        custom_resource_role.add_to_policy(iam.PolicyStatement(
            actions=["sts:AssumeRole"],
            resources=[batch_operations_role.role_arn]
        ))

        manifest_bucket_arn = f'arn:aws:s3:::{source_bucket_name}'
        report_bucket_arn = f'arn:aws:s3:::{source_bucket_name}'

        batch_resource = cr.AwsCustomResource(
            self,
            f"StartBatchJobResource-{bucket_hash}",
            on_create=cr.AwsSdkCall(
                service="S3Control",
                action="createJob",
                parameters={
                    "AccountId": cdk.Aws.ACCOUNT_ID,
                    "Operation": {
                        "S3ReplicateObject": {}
                    },
                    "ManifestGenerator":{
                        'S3JobManifestGenerator': {
                            'SourceBucket': manifest_bucket_arn,
                            'ManifestOutputLocation': {
                                'Bucket': manifest_bucket_arn,
                                'ManifestPrefix': 'auto-generated-manifest/',
                                'ManifestFormat': 'S3InventoryReport_CSV_20211130'
                            },
                            'EnableManifestOutput': True,
                            'Filter': {
                                'EligibleForReplication': True,
                                'MatchAnyStorageClass': [
                                    'STANDARD',
                                ]
                            },
                        }
                    },
                    "Report":{
                        'Bucket': report_bucket_arn,
                        'Format': 'Report_CSV_20180820',
                        'Enabled': True,
                        'Prefix': "batch-job-reports/",
                        'ReportScope': 'AllTasks'
                    },
                    "Priority":10,
                    "RoleArn":batch_operations_role.role_arn,
                    "Description":f'{source_bucket_name} to {destination_bucket_name}',
                    "ConfirmationRequired":False
                },
                physical_resource_id=cr.PhysicalResourceId.of(f"StartBatchJob-{bucket_hash}")
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=["s3:CreateJob"],
                    resources=["*"]
                ),
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    resources=[batch_operations_role.role_arn]
                ),
                iam.PolicyStatement(
                    actions=["iam:PassRole"],
                    resources=[batch_operations_role.role_arn] 
                )

            ]),
            # Assign the custom resource role to the custom resource
            role=custom_resource_role,
            timeout=cdk.Duration.minutes(30)
        )

