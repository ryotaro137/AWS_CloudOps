from aws_cdk import (
    App, Stack, Duration, CfnOutput,
    aws_lambda as _lambda
)
from constructs import Construct
import os

FUNC = """
import time
from random import choice, randint

def handler(event, context):
    time.sleep(randint(2,5))
    sushi = ["salmon", "tuna", "mackerel"]
    message = "Welcome to Cloud Sushi. Your order is " + choice(sushi)
    print(message)
    return message
"""

class SimpleLambda(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        handler = _lambda.Function(
            self, 'LambdaHandler',
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=_lambda.Code.from_inline(FUNC),
            memory_size=128,
            timeout=Duration.seconds(10),
            dead_letter_queue_enabled=True,
        )

        CfnOutput(self, "FunctionName", value=handler.function_name)

app = App()
SimpleLambda(
    app, "SimpleLambda",
    env={
        "region": os.environ.get("CDK_DEFAULT_REGION"),
        "account": os.environ.get("CDK_DEFAULT_ACCOUNT"), 
    }
)
app.synth()