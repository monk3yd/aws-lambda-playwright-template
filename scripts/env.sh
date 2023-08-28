#!/bin/bash
# Need to source this script for env variables to be available outside the context of the script
# command: source env.sh
# Remember to .gitignore this file when setup is done

export PROJECT_NAME="playwright-lambda-template"
echo "PROJECT_NAME is $PROJECT_NAME"

export AWS_ACCOUNT_ID="463185258187"
echo "AWS_ACCOUNT_ID is $AWS_ACCOUNT_ID"

export AWS_ACCESS_KEY_ID="AKIA6Q1BVK4JQP6VYM7K"
echo "AWS_ACCESS_KEY_ID is $AWS_ACCESS_KEY_ID"

export AWS_SECRET_ACCESS_KEY="xa89eAaMQIFgXHPgHD5Y0eBZinHGVuto0w5UXB3F"
echo "AWS_SECRET_ACCESS_KEY is $AWS_SECRET_ACCESS_KEY" 

export AWS_REGION_NAME="us-east-1"
echo "AWS_REGION_NAME is $AWS_REGION_NAME"

# export AWS_PROFILE=""
# echo "AWS_PROFILE is $AWS_PROFILE"

