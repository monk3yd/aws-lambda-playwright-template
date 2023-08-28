#!/bin/bash

### Build docker image & run docker container.

# Variables
IMAGE_NAME="lambda-template"
IMAGE_TAG="main"
CONTAINER_NAME="lambda-template-container"
HOST_MACHINE_PORT=9000
CONTAINER_PORT=8080

# Build docker image
# docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

# Use this instead when Dockerfile has own dir
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -f docker/Dockerfile .

# Run docker container locally
# -p : port mapping. This means that any traffic that goes through port 9000 on the host machine will be forwarded to port 8080 in the container. 
# --rm : tells docker to automatically remove the container when it stops running.
# -t : attaches tty to the container allowing to interact with it through the terminal.
docker run -p ${HOST_MACHINE_PORT}:${CONTAINER_PORT} --rm -t --name ${CONTAINER_NAME} ${IMAGE_NAME}:${IMAGE_TAG}
