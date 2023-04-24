# Deploying a WireGuard VPN Server with AWS SAM
This is a serverless application that allows you to deploy a WireGuard VPN server on AWS using AWS Serverless Application Model (SAM). SAM is an open-source framework for building serverless applications that provides shorthand syntax to express functions, APIs, databases, and event source mappings.

## Architecture Overview
The application architecture consists of an Auto Scaling group of EC2 instances running WireGuard VPN server. The EC2 instances are launched into a public subnet and are associated with an Elastic IP address. Users can connect to the VPN server using the Elastic IP address.

The following AWS resources are created:

* EC2 instance
* Elastic IP
* Launch template
* Security group
* VPC, subnet, and Internet Gateway
* Lambda function to create Wireguard keys for EC2 instance
* IAM role and instance profile for the EC2 instances
* Log group for Lambda function

## Prerequisites
Before you start deploying the application, make sure you have:

* AWS CLI installed and configured with your AWS account credentials
* AWS SAM CLI installed
* Docker installed

## Deployment
To deploy the application, follow the steps below:

1. Clone the repository: `git clone https://github.com/ovcharenko/aws-sam-wireguard.git`
2. Navigate to the cloned directory: `cd aws-sam-wireguard`
3. Build the Docker image for the Lambda function: `sam build`
4. Deploy the application: `sam deploy --guided`

The `sam deploy --guided` command will prompt you for the deployment options, including the AWS Region, Stack Name, and other parameters. Follow the prompts to deploy the application.

After the deployment is complete, you can connect to the VPN server using the Elastic IP address created by the CloudFormation stack. You can find the Elastic IP address in the CloudFormation stack outputs.

## Cleaning Up
To delete the application and all the AWS resources created by the CloudFormation stack, run the following command:

```bash
aws cloudformation delete-stack --stack-name <stack-name>
```

Replace <stack-name> with the name of the CloudFormation stack that was created during the deployment.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more information.
