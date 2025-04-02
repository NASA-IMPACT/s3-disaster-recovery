#!/usr/bin/env python3
import os

import aws_cdk as cdk
from dotenv import load_dotenv

from s3_disaster_recovery.s3_disaster_recovery_stack import S3DisasterRecoveryStack
from utils.hash_generator import generate_bucket_hash
load_dotenv()

app = cdk.App()
source_bucket_name = os.getenv("SOURCE_BUCKET_NAME") 
destination_bucket_name  = os.getenv("DESTINATION_BUCKET_NAME") 
bucket_hash = generate_bucket_hash(source_bucket_name, destination_bucket_name)
S3DisasterRecoveryStack(app, 
                        f"S3DisasterRecoveryStack-{bucket_hash}",
                        bucket_hash=bucket_hash
    )
app.synth()

