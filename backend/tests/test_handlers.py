"""
Unit tests for Lambda handler functions.
Uses moto to mock AWS services.
"""

import json
import os
import sys
import unittest
from unittest.mock import patch

import boto3
import pytest

# Provide a dummy TABLE_NAME before importing handlers
os.environ.setdefault("TABLE_NAME", "Books")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")

# ── Helpers ────────────────────────────────────────────────────────────────


def _make_table():
    """Create a mock DynamoDB Books table."""
    ddb = boto3.resource("dynamodb", region_name="us-east-1")
    table = ddb.create_table(
        TableName="Books",
        KeySchema=[{"AttributeName": "bookId", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "bookId", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    return table


# ── create_book ────────────────────────────────────────────────────────────


class TestCreateBook(unittest.TestCase):
    def setUp(self):
        from moto import mock_aws

        self.mock = mock_aws()
        self.mock.start()
        self.table = _make_table()

    def tearDown(self):
        self.mock.stop()

    def _invoke(self, body):
        # Re-import to pick up fresh boto3 client
        import importlib
        import handlers.create_book as m

        importlib.reload(m)
        event = {"body": json.dumps(body)}
        return m.handler(event, None)

    def test_create_valid_book(self):
        resp = self._invoke({"title": "Clean Code", "author": "Robert Martin"})
        assert resp["statusCode"] == 201
        data = json.loads(resp["body"])
        assert data["title"] == "Clean Code"
        assert "bookId" in data

    def test_create_missing_title(self):
        resp = self._invoke({"author": "Robert Martin"})
        assert resp["statusCode"] == 400

    def test_create_missing_author(self):
        resp = self._invoke({"title": "Clean Code"})
        assert resp["statusCode"] == 400

    def test_create_empty_body(self):
        import importlib
        import handlers.create_book as m

        importlib.reload(m)
        event = {"body": None}
        resp = m.handler(event, None)
        assert resp["statusCode"] == 400


# ── search_books ───────────────────────────────────────────────────────────


class TestSearchBooks(unittest.TestCase):
    def setUp(self):
        from moto import mock_aws

        self.mock = mock_aws()
        self.mock.start()
        self.table = _make_table()
        # Seed two books
        self.table.put_item(
            Item={
                "bookId": "1",
                "title": "Clean Code",
                "author": "Robert Martin",
                "isbn": "",
                "description": "",
                "createdAt": "2024-01-01T00:00:00+00:00",
            }
        )
        self.table.put_item(
            Item={
                "bookId": "2",
                "title": "The Pragmatic Programmer",
                "author": "David Thomas",
                "isbn": "",
                "description": "",
                "createdAt": "2024-01-02T00:00:00+00:00",
            }
        )

    def tearDown(self):
        self.mock.stop()

    def _invoke(self, query=None):
        import importlib
        import handlers.search_books as m

        importlib.reload(m)
        event: dict = {}
        if query is not None:
            event["queryStringParameters"] = {"q": query}
        return m.handler(event, None)

    def test_list_all_books(self):
        resp = self._invoke()
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert data["count"] == 2

    def test_search_by_title(self):
        resp = self._invoke("clean")
        data = json.loads(resp["body"])
        assert data["count"] == 1
        assert data["books"][0]["title"] == "Clean Code"

    def test_search_by_author(self):
        resp = self._invoke("david")
        data = json.loads(resp["body"])
        assert data["count"] == 1

    def test_search_no_results(self):
        resp = self._invoke("zzznomatch")
        data = json.loads(resp["body"])
        assert data["count"] == 0


# ── delete_book ────────────────────────────────────────────────────────────


class TestDeleteBook(unittest.TestCase):
    def setUp(self):
        from moto import mock_aws

        self.mock = mock_aws()
        self.mock.start()
        self.table = _make_table()
        self.table.put_item(
            Item={
                "bookId": "abc-123",
                "title": "Test Book",
                "author": "Test Author",
                "isbn": "",
                "description": "",
                "createdAt": "2024-01-01T00:00:00+00:00",
            }
        )

    def tearDown(self):
        self.mock.stop()

    def _invoke(self, book_id):
        import importlib
        import handlers.delete_book as m

        importlib.reload(m)
        event = {"pathParameters": {"bookId": book_id}}
        return m.handler(event, None)

    def test_delete_existing_book(self):
        resp = self._invoke("abc-123")
        assert resp["statusCode"] == 200

    def test_delete_nonexistent_book(self):
        resp = self._invoke("does-not-exist")
        assert resp["statusCode"] == 404

    def test_delete_missing_book_id(self):
        resp = self._invoke("")
        assert resp["statusCode"] == 400
