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
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )
app.synth()

