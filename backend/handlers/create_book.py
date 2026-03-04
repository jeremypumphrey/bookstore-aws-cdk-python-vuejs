"""
create_book.py – POST /books
Creates a new book in DynamoDB.

Expected JSON body:
{
    "title": "string",
    "author": "string",
    "isbn": "string",       (optional)
    "description": "string" (optional)
}
"""

import json
import os
import uuid
from datetime import datetime, timezone

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
        body = json.loads(event.get("body") or "{}")

        title = (body.get("title") or "").strip()
        author = (body.get("author") or "").strip()

        if not title or not author:
            return {
                "statusCode": 400,
                "headers": HEADERS,
                "body": json.dumps({"error": "title and author are required"}),
            }

        book = {
            "bookId": str(uuid.uuid4()),
            "title": title,
            "author": author,
            "isbn": (body.get("isbn") or "").strip(),
            "description": (body.get("description") or "").strip(),
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }

        table.put_item(Item=book)

        return {
            "statusCode": 201,
            "headers": HEADERS,
            "body": json.dumps(book),
        }

    except Exception as exc:  # pylint: disable=broad-except
        return {
            "statusCode": 500,
            "headers": HEADERS,
            "body": json.dumps({"error": str(exc)}),
        }
