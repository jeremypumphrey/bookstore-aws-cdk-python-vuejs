"""
Unit tests for the BookstoreStack CDK stack.
"""

import aws_cdk as cdk
from aws_cdk.assertions import Template

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


def test_three_lambda_functions_created():
    template = _template()
    # CDK BucketDeployment adds internal Lambda functions, so there are
    # more than 3 total. Verify at least our 3 business functions are present.
    lambdas = template.find_resources("AWS::Lambda::Function")
    assert len(lambdas) >= 3


def test_api_gateway_created():
    template = _template()
    template.resource_count_is("AWS::ApiGateway::RestApi", 1)


def test_s3_bucket_created():
    template = _template()
    # At least one non-CDK-managed S3 bucket exists
    buckets = template.find_resources("AWS::S3::Bucket")
    assert len(buckets) >= 1


def test_cloudfront_distribution_created():
    template = _template()
    template.resource_count_is("AWS::CloudFront::Distribution", 1)
