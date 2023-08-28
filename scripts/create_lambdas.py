### Create Lambda using boto3

import boto3
import json
import os

from loguru import logger
from utils import generate_role_name


# ------------- AWS Settings ----------------

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION_NAME = os.getenv("AWS_REGION_NAME")
PROJECT_NAME = os.getenv("PROJECT_NAME")

# Determines the source from where the lambda function will take its code and dependencies
# local : uploads source zip file from local system when creating lambda
# s3 : use prestored source zip file within S3
# ecr : use docker image saved within ECR repository
WORKFLOW: str = "ecr"

LAMBDA_NAME = PROJECT_NAME
LAMBDA_RUNTIME = "python3.11"
LAMBDA_HANDLER = "handler.app"
LAMBDA_TIMEOUT = 300  # 5min


# ======================================


def main():
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION_NAME,
    )

    iam_client = session.client("iam")
    lambda_client = session.client("lambda")

    role_name = generate_role_name(PROJECT_NAME)
    # Import IAM role for basic lambda execution
    role = iam_client.get_role(RoleName=f"LambdaBasicExecution{role_name}")

    if WORKFLOW == "local":
        # Upload directly zip code and dependencies
        with open("lambda.zip", "rb") as file:
            zipped_code = file.read()

        # upload zip file stored locally when creating lambda
        workflow_config = {"Code": {"ZipFile": zipped_code}, "PackageType": "Zip"}

    if WORKFLOW == "s3":
        # use zip file stored in S3 when creating lambda
        workflow_config = {
            "Code": {
                "S3Bucket": "roilab",
                "S3Key": "source/spider-api-manager-lambda.zip",
            },
            "PackageType": "Zip",
        }

        basic_config = {
            "FunctionName": LAMBDA_NAME,
            "Runtime": LAMBDA_RUNTIME,
            "Role": role["Role"]["Arn"],
            "Handler": LAMBDA_HANDLER,
            "Timeout": LAMBDA_TIMEOUT,  # Maximum allowable timeout
            # Set up Lambda function environment variables
            # "Environment": {
            #     "Variables": {"Name": "helloWorldLambda", "Environment": "prod"}
            # },
        }

    if WORKFLOW == "ecr":
        # TODO:
        # branches = ["main", "experimental"]
        branches = ["main"]
        for branch in branches:
            # Main lambda
            with open(f"scripts/data/ecr_repo_{branch}.txt", "r") as file:
                uri = file.read().strip()

            # use ECR docker image for building container for lambda function
            workflow_config = {"Code": {"ImageUri": uri}, "PackageType": "Image"}

            if branch == "main":
                lambda_function = LAMBDA_NAME
                filename = "lambda.json"

            if branch == "experimental":
                lambda_function = f"{LAMBDA_NAME}-experimental"
                filename = "lambda_experimental.json"

            basic_config = {
                "FunctionName": lambda_function,
                "Role": role["Role"]["Arn"],
                "Timeout": LAMBDA_TIMEOUT,  # Maximum allowable timeout
                # Set up Lambda function environment variables
                # "Environment": {
                #     "Variables": {"Name": "helloWorldLambda", "Environment": "prod"}
                # },
            }

            # Merge
            lambda_configuration = basic_config | workflow_config

            response = lambda_client.create_function(**lambda_configuration)
            logger.info(f"Lambda creation response: {response}")

            with open(f"scripts/data/{filename}", "w") as file:
                file.write(json.dumps(response))


if __name__ == "__main__":
    main()


## References
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/create_function.html
# https://hands-on.cloud/boto3-lambda-tutorial/
# https://stackoverflow.com/questions/67710230/how-to-deploy-aws-lambda-with-boto3-and-docker
