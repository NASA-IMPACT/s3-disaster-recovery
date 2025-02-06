# S3 Disaster Recovery

- Status: draft
- Deciders: [GHG Team](https://github.com/orgs/US-GHG-Center/teams/ghgc-all)
- Date: 2025-02-05
- Tags: AWS S3 Disaster-Recovery


## Context and Problem Statement

Several projects rely on Amazon S3 as the primary data store for critical functionality, including analysis and visualization. However, unforeseen events such as accidental deletions, data corruption, or regional outages pose significant risks to data availability and integrity. A robust disaster recovery (DR) strategy is essential to ensure that data remains accessible and recoverable in such scenarios.

To address this, various DR solutions must be evaluated based on cost, recovery time objectives (RTO), recovery point objectives (RPO), and compliance requirements. The ideal solution should balance redundancy, cost-effectiveness, and ease of maintenance while minimizing operational overhead through automation as much as possible.

## Decision Drivers <!-- optional -->


- Cost-effectiveness: Minimize costs while maintaining necessary redundancy.

- Data durability and availability: Ensure critical data is retrievable during outages.

- Recovery Time Objective (RTO) & Recovery Point Objective (RPO): How quickly can we recover? Vs How much data loss is acceptable?.

- Automation & maintenance overhead: Reduce manual intervention in the backup and restoration process.

- Compliance requirements: Ensure adherence to data retention policies.



## Considered Options

### Option 1: Cross-Region Replication (CRR) with Versioning (<span style="color:red">Most Costly</span>)
AWS Cross-Region Replication (CRR) is an Amazon S3 feature that automatically replicates objects from a source bucket in one AWS region to a destination bucket in a different AWS region. CRR ensures data redundancy, enhances disaster recovery, and improves data accessibility across geographically distributed locations.

CRR requires S3 Versioning to be enabled on both the source and destination buckets. Versioning helps retain multiple versions of an object, preventing accidental deletions or overwrites from permanently losing data.

#### How it works

1️⃣ Configuration

- Set up replication rules, defining whether the destination storage class transitions (e.g., Standard, Intelligent-Tiering, Glacier).

- Choose whether to replicate delete markers and configure Replication Time Control for predictable replication speeds.

2️⃣ Object Creation & Modification

- When a new object is uploaded, AWS S3:
 - Assigns a unique version ID.
 - Checks if it matches replication rules and, if so, copies it asynchronously to the destination bucket.
 - If an object is updated, a new version is created and replicated.

3️⃣ Object Deletion Handling

- If an object is deleted, a delete marker can optionally be replicated.
- If a specific object version is permanently deleted, it is not replicated unless explicitly configured.



### Option 2: S3 Same-Region Replication (SRR) with Versioning (<span style="color:red">Mid-Cost</span>)

AWS Same-Region Replication (SRR) is an Amazon S3 feature that automatically replicates objects within the same AWS region from a source bucket to a destination bucket. When Versioning is enabled, multiple versions of an object are maintained, allowing for data recovery in case of accidental overwrites or deletions.

SRR is particularly useful for data redundancy, compliance, access control, and backup management without the added latency and costs of cross-region replication.


#### How it works

1️⃣ Configuration

- Set up replication rules, defining whether the destination storage class transitions (e.g., Standard, Intelligent-Tiering, Glacier).

- Choose whether to replicate delete markers and configure Replication Time Control for predictable replication speeds.

2️⃣ Object Creation & Modification

- When a new object is uploaded, AWS S3:
    - Assigns a unique version ID.
    - Checks if it meets the replication rule conditions. If matched, the object is asynchronously copied to the destination bucket.
- When an object is updated, a new version is created and replicated.

3️⃣ Object Deletion Handling

- If an object is deleted, a delete marker can optionally be replicated.
- If a specific object version is permanently deleted, it is not replicated unless explicitly configured.


### Option 3: S3 Backup and Restore using AWS Backup (<span style="color:red">Affordable</span>)
AWS Backup is a fully managed backup service that provides centralized backup management across AWS services, including Amazon S3. By using AWS Backup, you can protect your S3 data by creating automated backup schedules, applying retention policies, and ensuring that your data can be restored efficiently in the event of data loss, corruption, or deletion. AWS Backup offers a simple and scalable solution for backing up large datasets and helps maintain data integrity with compliance controls for industries that require robust backup strategies.

#### How it works

1️⃣ Configuration

- Enable AWS Backup for S3 in your AWS account, and assign the specific S3 buckets you want to back up to the backup plan.

- Setting permissions and configuring the necessary IAM roles and policies to allow AWS Backup to access your S3 buckets.

- Create a backup plan that outlines the backup frequency, retention policies, and lifecycle management.

2️⃣ Backup Process

- Scheduled Backup: AWS Backup automatically takes snapshots of the S3 data according to the backup schedule. The data is backed up to the backup vault in the form of a consistent snapshot.
- Data Encryption: By default, AWS Backup encrypts backup data at rest using AWS Key Management Service (KMS) encryption keys.
- Incremental Backups: Only changes (new or modified objects) since the last backup are backed up, reducing backup storage costs and time.

3️⃣ Point-in-Time Restore

- Restore Data: In case of data loss or corruption, AWS Backup allows you to restore an entire S3 bucket or specific objects to a specific point in time (based on the backup schedule).
- Restore Options: You can restore the backup to the original S3 bucket or a different bucket (either in the same region or another region).
- Validation: Once the restore is complete, AWS Backup provides status updates, ensuring that the restore operation was successful and that the data integrity is maintained.


### Option 4: Periodic S3 Backups to Another Bucket (<span style="color:red">Cheap</span>)

Leverage the existing Self Managed Apache Airflow (SM2A) to orchestrate and automate the backup and restore process for S3 data. Airflow DAGs (Directed Acyclic Graphs) can be used to schedule and manage workflows that perform regular backups of S3 buckets to other S3 bucket.

#### How it works

1️⃣ Development & configuration

- Develop a DAG that defines the workflow for backing up S3 data. The DAG can include tasks for syncing the data to another S3 bucket.

- Add S3 event notification to trigger the DAG in case of an object deleted, created or updated.

- Add life cycle policy for the backup S3 

2️⃣ Object Creation & Modification

- If an object is created or updated an event notofication will trigger a lambda function which wil trigger the backup DAG which will copy the S3 object to another S3 bucket


3️⃣ Restoration

In case of accidental delete a lambda function for restoring the object will trigger the restore DAG which will restore the object and copy the file back to the original bucket. For permanent delete you will need to delete the backup object first



- 
## Decision Outcome

TBD

### Positive Consequences <!-- optional -->

- TBD

### Negative Consequences <!-- optional -->

- TBD

## Pros and Cons of the Options

### Option 1: Cross-Region Replication (CRR) with Versioning

#### Pros:
- Prevent Ransomware or Malicious Deletes
- Automated and fully managed by AWS.
- Protects against regional failures.
- Allows for immediate failover to another region.
- Storing data in multiple geographic locations.
- Users in different regions can access replicated data with lower latency.

#### Cons:
- High storage and replication costs.
- Adding data transfer, and request costs for replication and versioning.
- Requires proper policy configuration, versioning strategy, and lifecycle rules to avoid excessive costs.


### Option 2: S3 Same-Region Replication (SRR) with Versioning

#### Pros:
- Prevent Ransomware or Malicious Deletes
- Helps maintain a redundant copy of objects within the same region, increasing fault tolerance.
- Fatser recovery when compared to CRR (option 1).
- Provides protection against accidental deletions and corruption by maintaining versioned copies in another bucket.
- Can be combined with S3 Object Lock to prevent data tampering.


#### Cons:
- High storage and replication costs.
- Does not help in case of a full-region outage.
- Requires proper policy configuration, versioning strategy, and lifecycle rules to avoid excessive costs.


### Option 3: S3 Backup and Restore using AWS Backup

#### Pros:
- Prevent Ransomware or Malicious Deletes
- Helps maintain a redundant copy of objects within the same region, increasing fault tolerance.
- Fatser recovery when compared to CRR (option 1).
- Provides protection against accidental deletions and corruption by maintaining versioned copies in another bucket.
- Can be combined with S3 Object Lock to prevent data tampering.


#### Cons:
- High storage and replication costs.
- Does not help in case of a full-region outage.
- Requires proper policy configuration, versioning strategy, and lifecycle rules to avoid excessive costs.
