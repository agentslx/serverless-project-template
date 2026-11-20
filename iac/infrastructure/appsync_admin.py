"""Admin AppSync GraphQL API.

Separate API from the user-facing one because:
  • It's authed by the **admin** Cognito user pool (different JWT issuer).
  • Throttling, x-ray, WAF should be configured independently.
  • Schema/resolvers live next to the admin feature
    (`backend/feature/admin_rs/presentation/graphql_resolvers/`).

Currently exposes:
  - Query.listUsers — Lambda-backed paginated scan, gated to the `admin` group.
"""
from __future__ import annotations

import json
import os

import pulumi
import pulumi_aws as aws

# Resolve schema/resolver paths relative to this file → repo root.
_HERE = os.path.dirname(os.path.abspath(__file__))
_RESOLVERS_DIR = os.path.normpath(
    os.path.join(_HERE, "..", "..", "backend", "feature", "admin_rs",
                 "presentation", "graphql_resolvers")
)


def _read(p: str) -> str:
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


class AdminAppSyncApi:
    def __init__(self, prefix: str, stack: str, *, pools, list_users_lambda_arn):
        # 1. API — authed by the admin user pool.
        self.api = aws.appsync.GraphQLApi(
            f"{prefix}-{stack}-appsync-admin",
            name=f"{prefix}-{stack}-appsync-admin",
            authentication_type="AMAZON_COGNITO_USER_POOLS",
            user_pool_config=aws.appsync.GraphQLApiUserPoolConfigArgs(
                user_pool_id=pools.admin_pool.id,
                aws_region=aws.config.region,
                default_action="DENY",  # admin API is closed-by-default
            ),
            schema=_read(os.path.join(_RESOLVERS_DIR, "schema.graphql")),
            xray_enabled=True,
        )

        # 2. IAM role for AppSync to invoke the list_users Lambda.
        lambda_role = aws.iam.Role(
            f"{prefix}-{stack}-appsync-admin-lambda-role",
            assume_role_policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "appsync.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }],
            }),
        )
        aws.iam.RolePolicy(
            f"{prefix}-{stack}-appsync-admin-lambda-policy",
            role=lambda_role.id,
            policy=list_users_lambda_arn.apply(lambda a: json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": "lambda:InvokeFunction",
                    "Resource": a,
                }],
            })),
        )

        # 3. Lambda data source.
        list_users_ds = aws.appsync.DataSource(
            f"{prefix}-{stack}-ds-admin-list-users",
            api_id=self.api.id,
            name="ListUsersLambda",
            type="AWS_LAMBDA",
            service_role_arn=lambda_role.arn,
            lambda_config=aws.appsync.DataSourceLambdaConfigArgs(
                function_arn=list_users_lambda_arn,
            ),
        )

        # 4. JS resolver.
        aws.appsync.Resolver(
            f"{prefix}-{stack}-resolver-listUsers",
            api_id=self.api.id,
            type="Query",
            field="listUsers",
            data_source=list_users_ds.name,
            runtime=aws.appsync.ResolverRuntimeArgs(
                name="APPSYNC_JS",
                runtime_version="1.0.0",
            ),
            code=_read(os.path.join(_RESOLVERS_DIR, "listUsers.js")),
        )
