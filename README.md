# s3-disater-recovery
This repository provides a Cloud Development Kit (CDK) solution for implementing Same Region Replica (SRR) for S3 buckets as a disaster recovery mechanism. The stack automates replication configuration, batch replication of existing objects, and lifecycle management.

## Key Features
- *Replication Setup*: Automatically configures replication rules on the source bucket to copy new objects to the destination bucket.
- **Batch Replication**: Uses an S3 Batch Job to replicate pre-existing objects (optional).
- **Lifecycle Management**: Applies lifecycle rules to the destination bucket for cost optimization.
- **Resource Naming**: Generates unique resource names based on source/destination bucket hashes for multi-destination support.
- **Role Retention**: IAM roles persist after stack deletion, requiring manual cleanup

## Prerequisites
- **Existing S3 Buckets**: Source and destination buckets must be created beforehand with versioning enabled.
- **AWS Credentials**: Configured in .env (copy from .env_examples).

## Deployment
```
$ pip install -r requirements.txt
```
```
cp .env_examples .env
```
```
$ cdk synth
```
```
$ cdk deploy
```

## Manual Removal Required
Replication configurations and IAM roles are retained after stack deletion. To fully discontinue, manually remove:
- Replication rules from the source bucket.
- IAM roles created by the stack.
- Remove destination bucket (if required)