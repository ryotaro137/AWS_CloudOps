from enum import auto
from aws_cdk import (
    # Duration,
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    # aws_sqs as sqs,
)
from constructs import Construct

class CdkPythonS3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        s3.Bucket(self, "MyBucket",
         versioned=True,
         removal_policy=RemovalPolicy.DESTROY,
         auto_delete_objects=True
         )

        # example resource
        # queue = sqs.Queue(
        #     self, "CdkPythonS3Queue",
        #     visibility_timeout=Duration.seconds(300),
        # )
