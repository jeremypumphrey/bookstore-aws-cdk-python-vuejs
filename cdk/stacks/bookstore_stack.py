import os
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Tags,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    RemovalPolicy,
    CfnOutput,
    Duration,
)
from constructs import Construct


class BookstoreStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ── DynamoDB ──────────────────────────────────────────────────────────
        books_table = dynamodb.Table(
            self,
            "BooksTable",
            table_name="bookstore-books",
            partition_key=dynamodb.Attribute(
                name="bookId", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Add GSI for title search
        books_table.add_global_secondary_index(
            index_name="TitleIndex",
            partition_key=dynamodb.Attribute(
                name="title", type=dynamodb.AttributeType.STRING
            ),
        )

        # ── Shared Lambda configuration ───────────────────────────────────────
        lambda_env = {"TABLE_NAME": books_table.table_name}
        lambda_defaults = dict(
            runtime=lambda_.Runtime.PYTHON_3_12,
            timeout=Duration.seconds(30),
            memory_size=256,
            environment=lambda_env,
            code=lambda_.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "../../backend/handlers")
            ),
        )

        # ── Lambda functions ─────────────────────────────────────────────────
        create_book_fn = lambda_.Function(
            self,
            "CreateBookFunction",
            function_name="bookstore-create-book",
            handler="create_book.handler",
            description="Create a new book entry",
            **lambda_defaults,
        )

        search_books_fn = lambda_.Function(
            self,
            "SearchBooksFunction",
            function_name="bookstore-search-books",
            handler="search_books.handler",
            description="Search / list books",
            **lambda_defaults,
        )

        delete_book_fn = lambda_.Function(
            self,
            "DeleteBookFunction",
            function_name="bookstore-delete-book",
            handler="delete_book.handler",
            description="Delete a book by ID",
            **lambda_defaults,
        )

        # Grant DynamoDB permissions
        books_table.grant_write_data(create_book_fn)
        books_table.grant_read_data(search_books_fn)
        books_table.grant_write_data(delete_book_fn)

        # ── API Gateway ───────────────────────────────────────────────────────
        api = apigateway.RestApi(
            self,
            "BookstoreApi",
            rest_api_name="bookstore-api",
            description="Bookstore REST API",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"],
            ),
        )

        books_resource = api.root.add_resource("books")
        book_id_resource = books_resource.add_resource("{bookId}")

        books_resource.add_method(
            "POST", apigateway.LambdaIntegration(create_book_fn)
        )
        books_resource.add_method(
            "GET", apigateway.LambdaIntegration(search_books_fn)
        )
        book_id_resource.add_method(
            "DELETE", apigateway.LambdaIntegration(delete_book_fn)
        )

        # ── S3 bucket for Vue frontend ────────────────────────────────────────
        frontend_bucket = s3.Bucket(
            self,
            "FrontendBucket",
            bucket_name=cdk.Fn.join("-", ["bookstore-frontend", cdk.Aws.ACCOUNT_ID, cdk.Aws.REGION]),
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )

        # ── CloudFront distribution ───────────────────────────────────────────
        oac = cloudfront.S3OriginAccessControl(
            self,
            "OAC",
            origin_access_control_name="bookstore-oac",
            signing=cloudfront.Signing.SIGV4_NO_OVERRIDE,
        )

        distribution = cloudfront.Distribution(
            self,
            "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(
                    frontend_bucket, origin_access_control=oac
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
            ],
        )

        # ── Frontend deployment ───────────────────────────────────────────────
        s3deploy.BucketDeployment(
            self,
            "DeployFrontend",
            sources=[
                s3deploy.Source.asset(
                    os.path.join(
                        os.path.dirname(__file__), "../../frontend/dist"
                    )
                )
            ],
            destination_bucket=frontend_bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        # ── Outputs ───────────────────────────────────────────────────────────
        CfnOutput(self, "ApiUrl", value=api.url, description="API Gateway URL")
        CfnOutput(
            self,
            "CloudFrontUrl",
            value=f"https://{distribution.distribution_domain_name}",
            description="CloudFront Distribution URL",
        )
        CfnOutput(
            self,
            "FrontendBucketName",
            value=frontend_bucket.bucket_name,
            description="S3 Bucket for frontend",
        )

        # ── Tags ──────────────────────────────────────────────────────────────
        Tags.of(self).add("name", "bookstore")
