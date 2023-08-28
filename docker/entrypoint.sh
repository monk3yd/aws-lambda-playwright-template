#!/bin/sh
# For fixing entrypoint error go into docker container and use
# 'whereis python' command, and use that path result. 


if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then
  exec /usr/bin/aws-lambda-rie /usr/bin/python3 -m awslambdaric $@
else
  exec /usr/bin/python3 -m awslambdaric $@
fi
