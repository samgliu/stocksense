import os
import json
import boto3

lambda_client = boto3.client(
    "lambda", region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)


def invoke_scraper_lambda(domain: str) -> str:
    payload = {"url": domain}
    response = lambda_client.invoke(
        FunctionName=os.getenv("SCRAPER_LAMBDA_NAME", "scraper-lambda"),
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )
    result = json.loads(response["Payload"].read().decode("utf-8"))
    return result.get("text", "")


def invoke_gcs_lambda(query: str) -> list[str]:
    payload = {"query": query}
    response = lambda_client.invoke(
        FunctionName=os.getenv("GCS_LAMBDA_NAME", "gcs-lambda"),
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )
    raw = response["Payload"].read().decode("utf-8")
    body = json.loads(raw)
    data = json.loads(body["body"])
    return [f"{item['title']} {item['snippet']}" for item in data.get("results", [])]
