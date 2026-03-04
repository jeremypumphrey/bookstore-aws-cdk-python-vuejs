"""
delete_book.py – DELETE /books/{bookId}
Deletes a book from DynamoDB by its bookId.
"""

import json
import os

import boto3
from boto3.dynamodb.conditions import Key

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
        path_params = event.get("pathParameters") or {}
        book_id = path_params.get("bookId", "").strip()

        if not book_id:
            return {
                "statusCode": 400,
                "headers": HEADERS,
                "body": json.dumps({"error": "bookId path parameter is required"}),
            }

        # Verify book exists before deleting
        existing = table.get_item(Key={"bookId": book_id})
        if "Item" not in existing:
            return {
                "statusCode": 404,
                "headers": HEADERS,
                "body": json.dumps({"error": f"Book '{book_id}' not found"}),
            }

        table.delete_item(Key={"bookId": book_id})

        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps({"message": f"Book '{book_id}' deleted successfully"}),
        }

    except Exception as exc:  # pylint: disable=broad-except
        return {
            "statusCode": 500,
            "headers": HEADERS,
            "body": json.dumps({"error": str(exc)}),
        }
