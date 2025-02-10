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

### Option 1: Cross-Region Replication (CRR) with Versioning (<span style="color:red">High Cost</span>)
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



### Option 2: S3 Same-Region Replication (SRR) with Versioning (<span style="color:red">Affordable</span>)

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


### Option 3: S3 Backup and Restore using AWS Backup (<span style="color:red">Most Costly</span>)
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


### Option 4: Periodic S3 Backups to Another Bucket (<span style="color:red">Mid-Cost</span>)

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


## Cost Estimate of the Options
This section includes an estimate of the associated costs for maintaining 1TB of data. We are not including the cost of the source bucket because you will be paying that cost regardless of the chosen option.

### Disclamer 
The following cost estimates are based on standard AWS pricing as of the latest update and do not account for any future price changes or optimizations.

### Option 1: Cross-Region Replication (CRR) with Versioning
CRR involves replicating the data to a different AWS region, incurring additional storage and data transfer costs.
- Storage Costs:
    - 1TB in the destination bucket = 1024 GB
    - $0.023 per GB per month *1024 * 12  =  $282.62 per year
- Data Transfer Costs:
    - $0.02 per GB per month * 1024 = $245.76 per year
- API Request Costs:
    - ~ $60.00 per year (for PUT requests)
- Restore Costs:
    - $0.02 per GB per month * 1024 = $245.76 per year (Cross-Region Transfer Back to Original Region)

Total Annual Cost = <span style="color:red">$834.14 </span>  

### Option 2: S3 Same-Region Replication (SRR) with Versioning

SRR replicates data within the same region, eliminating cross-region transfer costs.
- Storage Costs:
    - 1TB in the destination bucket = 1024 GB
    - $0.023 per GB per month *1024 *12 = $282.62 per year
- Data Transfer Costs:
    - $0 (Replication within the same region is free)
- API Request Costs:
    - ~ $60.00 per year (for PUT requests)
- Restore Costs:
    - Free (Data is within the same region)
Total Annual Cost = <span style="color:red">$342.62</span>

### Option 3: S3 Backup and Restore using AWS Backup

AWS Backup provides automated backups with centralized management, compliance tracking, and vault storage.
- Storage Costs:
    - 1TB in the backup vault = 1024 GB
    - $0.05 per GB * 1024 *12  = $614.4 per year
- Data Transfer Costs:
    - N/A (Stored in AWS Backup vault)
- API Request Costs:
    - ~ $218.4 per year (for backup operations)
- Restore Costs:
    - $0.02 per GB * 1024 = $20.48 (restoring 1TB)

Total Annual Cost = <span style="color:red">$583.28 </span> 

### Option 4: Periodic S3 Backups to Another Bucket

This strategy uses an existing workflow to periodically copy data to another S3 bucket, including S3 event notifications and Lambda executions.
- Storage Costs:
    - 1TB in destination region = 1024 GB
    - Annual Cost: 1024 GB x 0.023/month *12 = $282.60
- API Request Costs:
    - ~ $60.00 per year (for PUT requests)
- S3 Event Notification:
    - Typically low or no cost, as S3 events themselves do not incur charges, but triggering services like Lambda might.
- Lambda Executions:
    - Assume 1 million requests per month and minimal compute time (e.g., 128MB, 100ms execution time per request)
    - Annual Request and Compute Cost: 1 million requests x 0.21/millionrequests * 12 = $2.52

Total Annual Cost = <span style="color:red">$345.12 </span>

## Estimated Cost Table

<table style="border-collapse: collapse; width: 100%; border: 1px solid #0000FF;">
  <thead>
    <tr style="background-color: #f2f2f2; border-bottom: 2px solid #0000FF;">
      <th style="border: 1px solid #0000FF; padding: 5px; text-align: center;">Backup Method</th>
      <th style="border: 1px solid #0000FF; padding: 5px; text-align: center;">Storage Cost (1 TB/year)</th>
      <th style="border: 1px solid #0000FF; padding: 5px; text-align: center;">Data Transfer Cost (Yearly)</th>
      <th style="border: 1px solid #0000FF; padding: 5px; text-align: center;">Compute Cost (Airflow, etc.)</th>
      <th style="border: 1px solid #0000FF; padding: 5px; text-align: center;">API Request Cost (Yearly)</th>
      <th style="border: 1px solid #0000FF; padding: 5px; text-align: center;">Restore Cost per TB</th>
      <th style="border: 1px solid #0000FF; padding: 5px; text-align: center;">Total Annual Cost</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom: 1px solid #0000FF;">
      <td style="border: 1px solid #0000FF; padding: 5px;"> <strong>Option 1: Cross-Region Replication (CRR) with Versioning</strong> </td>
      <td style="border: 1px solid #0000FF; padding: 5px;">$282.62</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">$245.76</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">N/A</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">$60 (PUT requests)</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">$245.76</td>
      <td style="border: 1px solid #0000FF; padding: 5px;"><span style="color:red">$834.14</span></td>
    </tr>
    <tr style="border-bottom: 1px solid #0000FF;">
      <td style="border: 1px solid #0000FF; padding: 5px;"> <strong>Option 2: S3 Same-Region Replication (SRR) with Versioning</strong> </td>
      <td style="border: 1px solid #0000FF; padding: 5px;">$282.62</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">$0</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">N/A</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">$60 (PUT requests)</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">Free</td>
      <td style="border: 1px solid #0000FF; padding: 5px;"><span style="color:red">$342.62</span></td>
    </tr>
    <tr style="border-bottom: 1px solid #0000FF;">
      <td style="border: 1px solid #0000FF; padding: 5px;"> <strong>Option 3: S3 Backup and Restore using AWS Backup</strong> </td>
      <td style="border: 1px solid #0000FF; padding: 5px;">$614.4</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">N/A</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">N/A</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">$218.4 (Backup API)</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">$20.48</td>
      <td style="border: 1px solid #0000FF; padding: 5px;"><span style="color:red">$853.28</span></td>
    </tr>
    <tr>
      <td style="border: 1px solid #0000FF; padding: 5px;"> <strong>Option 4: Periodic S3 Backups to Another Bucket</strong> </td>
      <td style="border: 1px solid #0000FF; padding: 5px;">$282.60</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">$0</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">N/A (Reusing SM2A workers)</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">$62.52 (PUT requests + Lambda)</td>
      <td style="border: 1px solid #0000FF; padding: 5px;">Free</td>
      <td style="border: 1px solid #0000FF; padding: 5px;"><span style="color:red">$345.14</span></td>
    </tr>
  </tbody>
</table>


## Pros and Cons of the Options

### Option 1: S3 Cross-Region Replication (CRR) with Versioning

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
- Replicating existing objects needs custom configuration (S3 Batch Replication)
- Need to develop a logic of the restoration.


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
- Replicating existing objects needs custom configuration (S3 Batch Replication).
- Need to develop a logic of the restoration. 


### Option 3: S3 Backup and Restore using AWS Backup

#### Pros:
- Prevent Ransomware or Malicious Deletes
- Helps maintain a redundant copy of objects within the same region, increasing fault tolerance.
- Fatser recovery when compared to CRR (option 1).
- Provides protection against accidental deletions and corruption by maintaining versioned copies in another bucket.
- Can be combined with S3 Object Lock to prevent data tampering.


#### Cons:
- The most expensive option.
- High storage and replication costs.
- Does not help in case of a full-region outage.
- Requires proper policy configuration, versioning strategy, and lifecycle rules to avoid excessive costs.



### Option 4: Periodic S3 Backups to Another Bucket
#### Pros:
- More control over backup frequency and storage.
- Ability to filter and backup only necessary objects instead of the entire bucket..
- Can choose whether to store backups in the same or different cloud accounts (or on-prem).
- Airflow can monitor and retry failed backup tasks for reliability.


#### Cons:
- Requires monitoring and maintaining Airflow DAGs and Lambda functions.
- If backup frequency is too low, recent changes may not be included in the latest backup.
- Copying large volumes of data periodically may impact performance of Airflow


## Links
- [s3-backup](https://n2ws.com/blog/aws-cloud/s3-backup)
- [s3-pricing](https://aws.amazon.com/s3/pricing/)
- [s3-backup-pricing](https://aws.amazon.com/backup/pricing/)
- [s3-replication](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html)
