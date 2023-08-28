# aws-lambda-template

## Steps to follow for CICD setup:

Create a new lambda project github repository by using [aws-lambda-template](https://github.com/monk3yd/aws-lambda-template)

Clone new lambda project github repository into local machine 
The project name in this example is: github-to-lambda
```bash
git clone git@github.com:monk3yd/github-to-lambda.git
```

Setup virtual environment
Note: Last supported python version for lambda is python3.9, for newer versions we need to add custom runtime when creating docker image.

- VIRTUALENV:
```bash
pip3 install virtualenv

# This will create a new directory called myenv in your current directory, which contains a new Python environment.
virtualenv myenv

# create venv dir with specific version of Python taken from conda
virtualenv -p ~/anaconda3/bin/python3.9 venv

# This will activate the virtual environment and change your shell's prompt to indicate that you're using the new environment.
source myenv/bin/activate 
```

- CONDA:
```bash
conda create -n myenv python=3.11
conda activate myenv
```

Install required dependencies
```bash
pip3 install -r requirements.txt
```

Declare environment variables for setup configuration
```bash
export PROJECT_NAME="github-to-lambda"
export AWS_PROFILE="monk3yd"
export AWS_ACCOUNT_ID="134284459147"
export AWS_ACCESS_KEY_ID="aaabbcc0001122233"
export AWS_SECRET_ACCESS_KEY="aaabbcc0001122233"
export AWS_REGION_NAME="us-east-1"
```

Create ECR for new lambda project
```bash
bash scripts/create-ecr-repo.sh
```

Deploy init docker images (main/experimental) to ECR
```bash
bash scripts/deploy-images-to-ecr.sh
```

Create project IAM role for lambda
```bash
python3 scripts/create_iam_lambda_execution_role.py
```

Create lambda functions (main/experimental) and link them to respective image within ECR
```bash
python3 scripts/create_lambdas.py
```

Define github actions secrets within project repository:
  - PROJECT_NAME
  - AWS_ACCOUNT_ID
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_REGION_NAME

Push to main or experimental branches within github, the lambda function will update accordingly

## API Gateway Configuration

Create REST API in API Gateway through AWS console
> Now we need to configure the integration point for our request methods. To use a Lambda function as our integration point for ANY type of request (i.e., GET, POST, PATCH, DELETE, etc.), we will create a Method (to handle the root path) and a child Resource (to handle all child paths). We will configure them to handle any requests made to API Gateway by using the Lambda proxy integration [1].
  - Create method
  - Create resource

Configure lambda function as a proxy to forward requests from API Gateway to Amazon Lambda

Deploy API
> Since our Lambda is now configured, we can deploy the API. We can name it dev stage. The deployment is crucial to make the Lambda function integration active.

Configure methods & resources to require API key

Create API key

Create API usage plan

Redeploy

Activate CORS for methods & resources

Redeploy

## Resources
See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.
Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)


## [Docker Best Practices](https://www.youtube.com/watch?v=8vXoMqWgbQQ&list=WL&index=69)

1. Use official and verified docker images as base images
- Try to avoid OS docker images
- https://hub.docker.com/_/ubuntu
```Dockerfile
FROM docker pull ubuntu:latest
```

- Prefer specific images
- https://hub.docker.com/_/python
```Dockerfile
FROM docker pull python:latest
```

2. Use specific docker image versions 
- The more specific the better
```Dockerfile
FROM docker pull python:3.11.4
```

3. Use small sized official images
- Larger images (OS) bring tools you won't end up using
- It will also create a larger attack surface for possible vulnerabilities
- So, if you don't require specific system utilities or libraries choose
the leaner and smaller OS image
```Dockerfile
FROM docker pull python:3.11.4-alpine3.18
```

# 4. Optimize image layer cache when building
- Each command in a dockerfile creates an image layer
- Docker caches each layer into local filesystem
- Once a layer changes, all following layers are re-created as well
- Order commands from least to most frequently changing

5. Create .dockerignore in root dir to explicitly exclude 
files and folders from the build process

6. Use multi-stage builds
- Remove build dependencies and tools, final image only contains
runtime requirements

7. Use the Least Privileged User 
- Create a dedicated group and user
```Dockerfile
RUN groupadd -r tom && useradd -g tom tom
```

- Set ownership and permissions
```Dockerfile
RUN chown -R tom:tom /app
```

- Change to non-root user with USER directive
Some base images already have a generic user bundled in
```Dockerfile
USER tom
```

8. Scan images for security vulnerabilities (docker scan)
- CLI scan
- Dockerhub scan (automatically when image gets pushed)
- View scan summary via Dockerhub or Docker Desktop
- Build this scan into CICD pipeline

