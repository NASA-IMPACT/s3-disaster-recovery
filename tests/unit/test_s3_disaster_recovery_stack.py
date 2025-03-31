import aws_cdk as core
import aws_cdk.assertions as assertions

from s3_disaster_recovery.s3_disaster_recovery_stack import S3DisasterRecoveryStack

# example tests. To run these tests, uncomment this file along with the example
# resource in s3_disaster_recovery/s3_disaster_recovery_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = S3DisasterRecoveryStack(app, "s3-disaster-recovery")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
