# AWS Lambda Playwright Template

import os
# import json
import requests

from loguru import logger


def lambda_handler(event=dict(), context=dict()):
    logger.debug(f"Event: {event}")

    # Access input value
    machine = event["machine"]
    logger.debug(f"Machine name: {machine}")

    # Access environment value (Dockerfile)
    key = os.getenv("KEY")
    logger.debug(f"Key: {key}")

    try:
        ip = requests.get("http://checkip.amazonaws.com/")
    except requests.RequestException as error:
        # Send some context about this error to Lambda Logs
        logger.error(error)
        raise error
    else:
        logger.debug(f"My IP: {ip.text}")

    # 200OK lambda response
    return {
        "statusCode": 200,
        "headers": CORS,
        "body": {
            "message": "hello world",
            "location": ip.text.replace("\n", "")
        },
    }


# --- Local ---
# Run: python3 handler/app.py
if __name__ == "__main__":
    payload = {
        "machine": "monk3yd",
    }
    lambda_response = lambda_handler(event=payload)
    logger.info(f"Lambda response {type(lambda_response)}: {lambda_response}")

# --- Serverless ---
# Run: bash scripts/deploy-images-to-ecr.sh

