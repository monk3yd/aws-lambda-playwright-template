# Playwright Docker Image

# Using an alternative base image (python) with the runtime interface client (awslambdaric)
# https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions

# Define custom function directory
ARG FUNCTION_DIR="/home/monk3yd/"

# FROM python:3.11 as build-image
FROM mcr.microsoft.com/playwright/python:v1.37.0-jammy as build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR
RUN mkdir -p ${FUNCTION_DIR}

# Set environment variables
# ENV KEY=RFTL

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

COPY requirements.txt ${FUNCTION_DIR}
RUN pip install -r ${FUNCTION_DIR}/requirements.txt

# Copy function code
COPY ./handler/main.py ${FUNCTION_DIR}
COPY ./handler/vehicle_data_extractor.py ${FUNCTION_DIR}
# COPY ./handler/dead_or_alive.py ${FUNCTION_DIR}
# COPY ./handler/spider_manager.py ${FUNCTION_DIR}

# RUN pip install playwright --target ${FUNCTION_DIR}
# RUN python -m playwright install chromium
# RUN python -m playwright install-deps chromium

# Install the function's dependencies
RUN pip install \
    --target ${FUNCTION_DIR} \
        awslambdaric

# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
COPY docker/entrypoint.sh /
RUN chmod 755 /usr/bin/aws-lambda-rie /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

# Pass the name of the function handler as an argument to the runtime
CMD [ "main.lambda_handler" ]
