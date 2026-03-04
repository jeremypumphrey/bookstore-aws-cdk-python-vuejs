"""
Unit tests for the BookstoreStack CDK stack.
"""

import aws_cdk as cdk
from aws_cdk.assertions import Template, Match

from stacks.bookstore_stack import BookstoreStack


def _template() -> Template:
    app = cdk.App()
    stack = BookstoreStack(app, "TestBookstoreStack")
    return Template.from_stack(stack)


def test_dynamodb_table_created():
    template = _template()
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "KeySchema": [{"AttributeName": "bookId", "KeyType": "HASH"}],
            "BillingMode": "PAY_PER_REQUEST",
        },
    )


def test_dynamodb_table_name_prefixed():
    template = _template()
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {"TableName": "bookstore-books"},
    )


def test_three_lambda_functions_created():
    template = _template()
    # CDK BucketDeployment adds internal Lambda functions, so there are
    # more than 3 total. Verify at least our 3 business functions are present.
    lambdas = template.find_resources("AWS::Lambda::Function")
    assert len(lambdas) >= 3


def test_lambda_function_names_prefixed():
    template = _template()
    for name in ("bookstore-create-book", "bookstore-search-books", "bookstore-delete-book"):
        template.has_resource_properties(
            "AWS::Lambda::Function",
            {"FunctionName": name},
        )


def test_api_gateway_created():
    template = _template()
    template.resource_count_is("AWS::ApiGateway::RestApi", 1)


def test_api_gateway_name_prefixed():
    template = _template()
    template.has_resource_properties(
        "AWS::ApiGateway::RestApi",
        {"Name": "bookstore-api"},
    )


def test_s3_bucket_created():
    template = _template()
    # At least one non-CDK-managed S3 bucket exists
    buckets = template.find_resources("AWS::S3::Bucket")
    assert len(buckets) >= 1


def test_s3_bucket_name_prefixed():
    template = _template()
    # Bucket name uses Fn::Join with account/region tokens for uniqueness.
    # Verify the join array starts with the required "bookstore-frontend" prefix.
    template.has_resource_properties(
        "AWS::S3::Bucket",
        {
            "BucketName": Match.object_like(
                {"Fn::Join": Match.array_with(["-", Match.array_with(["bookstore-frontend"])])}
            )
        },
    )


def test_cloudfront_distribution_created():
    template = _template()
    template.resource_count_is("AWS::CloudFront::Distribution", 1)


def test_cloudfront_oac_name_prefixed():
    template = _template()
    template.has_resource_properties(
        "AWS::CloudFront::OriginAccessControl",
        {
            "OriginAccessControlConfig": Match.object_like(
                {"Name": "bookstore-oac"}
            )
        },
    )


def test_resources_tagged_with_name_bookstore():
    template = _template()
    # DynamoDB table should carry the stack-level tag
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {"Tags": Match.array_with([{"Key": "name", "Value": "bookstore"}])},
    )
    # Lambda functions should carry the stack-level tag
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {"Tags": Match.array_with([{"Key": "name", "Value": "bookstore"}])},
    )
    # API Gateway should carry the stack-level tag
    template.has_resource_properties(
        "AWS::ApiGateway::RestApi",
        {"Tags": Match.array_with([{"Key": "name", "Value": "bookstore"}])},
    )
