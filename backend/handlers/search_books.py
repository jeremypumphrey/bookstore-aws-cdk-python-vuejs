"""
search_books.py – GET /books
Lists or searches books in DynamoDB.

Query string parameters (all optional):
  q  – free-text search against title and author (case-insensitive contains)
"""

import json
import os

import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE",
}


def handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        query = (params.get("q") or "").strip().lower()

        if query:
            response = table.scan()
            all_items = response.get("Items", [])
            items = [
                item
                for item in all_items
                if query in item.get("title", "").lower()
                or query in item.get("author", "").lower()
                or query in item.get("isbn", "").lower()
            ]
        else:
            response = table.scan()
            items = response.get("Items", [])

        books = sorted(
            items,
            key=lambda b: b.get("createdAt", ""),
            reverse=True,
        )

        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps({"books": books, "count": len(books)}),
        }

    except Exception as exc:  # pylint: disable=broad-except
        return {
            "statusCode": 500,
            "headers": HEADERS,
            "body": json.dumps({"error": str(exc)}),
        }
