#!/bin/bash

### Create ECR repository in AWS.

# Variables
ACCOUNT_ID=${AWS_ACCOUNT_ID}
REGION_NAME=${AWS_REGION_NAME}
ECR_NAME=${PROJECT_NAME}

# Login
aws ecr get-login-password --region ${REGION_NAME} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION_NAME}.amazonaws.com

# Create ECR (Elastic Container Registry)
aws ecr create-repository  --region ${REGION_NAME} --repository-name ${ECR_NAME} --image-tag-mutability MUTABLE --image-scanning-configuration scanOnPush=false
