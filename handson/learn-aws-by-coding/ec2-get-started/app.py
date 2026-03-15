import aws_cdk as cdk  # core の代わりに cdk としてインポート
import os

from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class MyFirtstEc2(cdk.Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # 2. コンテキストから値を取り出す
        key_name = self.node.try_get_context("key_name")

        vpc = ec2.Vpc(self, "MyVpc", max_azs=1,
        cidr="10.0.0.0/23",
        subnet_configuration=[
            ec2.SubnetConfiguration(
                name="Public",
                subnet_type=ec2.SubnetType.PUBLIC
            )
        ],nat_gateways=0,
        )

        sg = ec2.SecurityGroup(
            self, "MySecurityGroup", 
            vpc=vpc,
        description="Allow SSH access to EC2 instances",
        allow_all_outbound=True,
        )
        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(), 
            connection=ec2.Port.tcp(22), 
            description="Allow SSH access"
        ) 

        host = ec2.Instance(self, "MyInstance", 
        instance_type=ec2.InstanceType("t3.micro"), 
        machine_image=ec2.MachineImage.latest_amazon_linux2(), 
        vpc=vpc, 
        vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        security_group=sg,
        key_name=key_name
        )

        cdk.CfnOutput(self, "InstanceId", value=host.instance_id)
        cdk.CfnOutput(self, "PublicIp", value=host.instance_public_ip)
        cdk.CfnOutput(self, "PublicDnsName", value=host.instance_public_dns_name)
    
app = cdk.App()
MyFirtstEc2(
    app, "MyFirtstEc2",
    env={
        "region": os.environ["CDK_DEFAULT_REGION"],
        "account": os.environ["CDK_DEFAULT_ACCOUNT"],
    }
)

app.synth()