#cdk deploy --profile ghgc-smce-mfa
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    RemovalPolicy,
    Duration,
    custom_resources as cr,
    CfnOutput
)
import aws_cdk as cdk
from constructs import Construct
from dotenv import load_dotenv
import os
from .setup_replication import SetUpReplication
from .add_lifecycle_rule import AddLifeCycleRule
from .start_batch_job import StartBatchJob

class S3DisasterRecoveryStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, bucket_hash: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.bucket_hash = bucket_hash 

        # Load environment variables
        load_dotenv()
        source_bucket_name = os.getenv("SOURCE_BUCKET_NAME") 
        destination_bucket_name = os.getenv("DESTINATION_BUCKET_NAME") 
        allow_batch_replication = os.getenv("ALLOW_BATCH_REPLICATION","false").lower() == "true" 
        permissions_boundary_policy_name = os.getenv("PERMISSIONS_BOUNDARY_POLICY_NAME", "")
        aws_account_id = os.getenv("AWS_ACCOUNT_ID", "")

        if permissions_boundary_policy_name and aws_account_id:
            permissions_boundary_arn = f"arn:aws:iam::{aws_account_id}:policy/{permissions_boundary_policy_name}"
        else:
            permissions_boundary_arn = ""

        print("from env source bucket: ", source_bucket_name)
        print("from env source bucket: ", destination_bucket_name)
        print("from env allow_batch_replication: ", allow_batch_replication)
        print("permission_boundary_arn: ",permissions_boundary_arn)
        
        if not source_bucket_name or not destination_bucket_name:
            raise ValueError("SOURCE_BUCKET_NAME and DESTINATION_BUCKET_NAME environment variable must be set")
        
        # Reference the existing source bucket
        source_bucket = s3.Bucket.from_bucket_name(
            self,
            f"ExistingSourceBucket-{self.bucket_hash}" ,
            source_bucket_name
        )

        # Reference the dest source bucket
        destination_bucket = s3.Bucket.from_bucket_name(
            self,
            f"ExistingDestinationBucket-{self.bucket_hash}",
            destination_bucket_name
        )

        #set_replication = SetUpReplication(self, f"SetUpReplication-{self.bucket_hash}", source_bucket, destination_bucket, source_bucket_name, destination_bucket_name, self.bucket_hash, permissions_boundary_arn )
    
        add_lifecyle = AddLifeCycleRule(self, f"AddLifeCycleRule-{self.bucket_hash}", destination_bucket_name, self.bucket_hash, permissions_boundary_arn)

        # if allow_batch_replication:
        #     start_batch = StartBatchJob(self, f"StartBatchJob-{self.bucket_hash}", source_bucket, destination_bucket, source_bucket_name, destination_bucket_name, self.bucket_hash, permissions_boundary_arn)

        # # Output Source Bucket Name
        # CfnOutput(self, f"SourceBucketName-{self.bucket_hash}",
        #     value=source_bucket_name,
        #     description="The name of the source S3 bucket."
        # )

        # # Output Destination Bucket Name
        # CfnOutput(self, f"DestinationBucketName-{self.bucket_hash}",
        #     value=destination_bucket_name,
        #     description="The name of the destination S3 bucket."
        # )


