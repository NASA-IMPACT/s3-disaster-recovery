#cdk deploy --profile ghgc-smce-mfa
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    RemovalPolicy,
    Duration,
    custom_resources as cr
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

        print("from env source bucket: ", source_bucket_name)
        print("from env source bucket: ", destination_bucket_name)
        print("from env allow_batch_replication: ", allow_batch_replication)
        
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

        set_replication = SetUpReplication(self, f"SetUpReplication-{self.bucket_hash}", source_bucket, destination_bucket, source_bucket_name, destination_bucket_name, self.bucket_hash)
    
        add_lifecyle = AddLifeCycleRule(self, f"AddLifeCycleRule-{self.bucket_hash}", destination_bucket_name, self.bucket_hash)

        if allow_batch_replication:
            start_batch = StartBatchJob(self, f"StartBatchJob-{self.bucket_hash}", source_bucket, destination_bucket, source_bucket_name, destination_bucket_name, self.bucket_hash)
