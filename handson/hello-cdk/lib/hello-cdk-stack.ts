import * as cdk from 'aws-cdk-lib/core';
import { Construct } from 'constructs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

export class HelloCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    // 1. Lambda関数を作成する指示
    const helloFunction = new lambda.Function(this, 'HelloHandler', {
      runtime: lambda.Runtime.NODEJS_20_X, // 動かす環境（おまじないとしてそのままでOK）
      code: lambda.Code.fromAsset('lib'),  // 「lib」フォルダの中身をAWSにアップロードする
      handler: 'hello.handler'             // 「hello.js」の「handler」を動かすという指定
    });
    // 2. API Gateway（インターネットからの受付窓口）を作成する指示
    new apigateway.LambdaRestApi(this, 'Endpoint', {
      handler: helloFunction               // 窓口に来た人を、さきほどのLambdaに案内する
    });
  }
}
