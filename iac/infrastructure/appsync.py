"""AppSync GraphQL API + DynamoDB direct data source + JS resolvers."""
from __future__ import annotations

import os
import pulumi
import pulumi_aws as aws

# Resolve schema/resolver paths relative to this file → repo root.
_HERE = os.path.dirname(os.path.abspath(__file__))
_RESOLVERS_DIR = os.path.normpath(
    os.path.join(_HERE, "..", "..", "backend", "feature", "user_profile_rs",
                 "presentation", "graphql_resolvers")
)


def _read(p: str) -> str:
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


class AppSyncApi:
    def __init__(self, prefix: str, stack: str, *, table, pools, user_profile_lambda_arn):
        # 1. API
        self.api = aws.appsync.GraphQLApi(
            f"{prefix}-{stack}-appsync",
            name=f"{prefix}-{stack}-appsync",
            authentication_type="AMAZON_COGNITO_USER_POOLS",
            user_pool_config=aws.appsync.GraphQLApiUserPoolConfigArgs(
                user_pool_id=pools.user_pool.id,
                aws_region=aws.config.region,
                default_action="ALLOW",
            ),
            schema=_read(os.path.join(_RESOLVERS_DIR, "schema.graphql")),
            xray_enabled=True,
        )

        # 2. IAM role for AppSync to talk to DynamoDB
        ddb_role = aws.iam.Role(
            f"{prefix}-{stack}-appsync-ddb-role",
            assume_role_policy=pulumi.Output.from_input({
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow",
                               "Principal": {"Service": "appsync.amazonaws.com"},
                               "Action": "sts:AssumeRole"}],
            }).apply(lambda d: __import__("json").dumps(d)),
        )
        aws.iam.RolePolicy(
            f"{prefix}-{stack}-appsync-ddb-policy",
            role=ddb_role.id,
            policy=pulumi.Output.all(table.arn).apply(lambda a: __import__("json").dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:GetItem", "dynamodb:Query",
                        "dynamodb:PutItem", "dynamodb:UpdateItem",
                    ],
                    "Resource": [a[0]],
                }],
            })),
        )

        # 3. DynamoDB direct data source (used by getUserProfile)
        ddb_ds = aws.appsync.DataSource(
            f"{prefix}-{stack}-ds-ddb",
            api_id=self.api.id,
            name="UserProfilesTable",
            type="AMAZON_DYNAMODB",
            service_role_arn=ddb_role.arn,
            dynamodb_config=aws.appsync.DataSourceDynamodbConfigArgs(
                table_name=table.name,
                region=aws.config.region,
            ),
        )

        # 4. Lambda data source (used by updateUserProfile)
        lambda_role = aws.iam.Role(
            f"{prefix}-{stack}-appsync-lambda-role",
            assume_role_policy=__import__("json").dumps({
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow",
                               "Principal": {"Service": "appsync.amazonaws.com"},
                               "Action": "sts:AssumeRole"}],
            }),
        )
        aws.iam.RolePolicy(
            f"{prefix}-{stack}-appsync-lambda-policy",
            role=lambda_role.id,
            policy=user_profile_lambda_arn.apply(lambda a: __import__("json").dumps({
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow", "Action": "lambda:InvokeFunction", "Resource": a}],
            })),
        )
        lambda_ds = aws.appsync.DataSource(
            f"{prefix}-{stack}-ds-lambda-update",
            api_id=self.api.id,
            name="UpdateProfileLambda",
            type="AWS_LAMBDA",
            service_role_arn=lambda_role.arn,
            lambda_config=aws.appsync.DataSourceLambdaConfigArgs(
                function_arn=user_profile_lambda_arn,
            ),
        )

        # 5. JS resolvers (APPSYNC_JS runtime)
        aws.appsync.Resolver(
            f"{prefix}-{stack}-resolver-getUserProfile",
            api_id=self.api.id,
            type="Query",
            field="getUserProfile",
            data_source=ddb_ds.name,
            runtime=aws.appsync.ResolverRuntimeArgs(
                name="APPSYNC_JS",
                runtime_version="1.0.0",
            ),
            code=_read(os.path.join(_RESOLVERS_DIR, "getUserProfile.js")),
        )
        aws.appsync.Resolver(
            f"{prefix}-{stack}-resolver-updateUserProfile",
            api_id=self.api.id,
            type="Mutation",
            field="updateUserProfile",
            data_source=lambda_ds.name,
            runtime=aws.appsync.ResolverRuntimeArgs(
                name="APPSYNC_JS",
                runtime_version="1.0.0",
            ),
            code=_read(os.path.join(_RESOLVERS_DIR, "updateUserProfile.js")),
        )
