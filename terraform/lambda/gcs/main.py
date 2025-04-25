import json
import os

import requests

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
GOOGLE_CX_ID = os.environ["GOOGLE_CX_ID"]


def lambda_handler(event, context):
    try:
        query = None
        if "body" in event:
            body = json.loads(event["body"])
            query = body.get("query")
        elif "query" in event:
            query = event["query"]

        if not query:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'query' in body"}),
            }

        # Google CSE API
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CX_ID,
            "q": query,
            "num": 10,
            "dateRestrict": "w2",
            "sort": "date",
        }

        res = requests.get(url, params=params)
        items = res.json().get("items", [])

        results = [
            {
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "link": item.get("link", ""),
            }
            for item in items
        ]

        return {
            "statusCode": 200,
            "body": json.dumps({"results": results}),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
