"""Chat Lambda functions — WebSocket handlers + REST history endpoints.

ws_send_message uses a Docker image (ECR) due to Strands SDK dependencies.
Other handlers use standard zip packaging (boto3 only).
"""
from __future__ import annotations

import json
import os
import pulumi
import pulumi_aws as aws


def _trust_policy() -> str:
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }],
    })


class ChatLambdas:
    """All Lambda functions for the research chat feature.

    Args:
        prefix: Project prefix.
        stack: Stack name (dev/prod).
        conversations_table_name: Name of the conversations DynamoDB table.
        conversations_table_arn: ARN of the conversations table.
        connections_table_name: Name of the WS connections DynamoDB table.
        connections_table_arn: ARN of the connections table.
        reports_bucket_name: Name of the S3 reports bucket.
        reports_bucket_arn: ARN of the S3 reports bucket.
        ws_management_endpoint: HTTPS endpoint for @connections API.
        appconfig_app_id: AppConfig application ID.
        appconfig_env_id: AppConfig environment ID.
        appconfig_profile_id: AppConfig configuration profile ID.
        ecr_image_uri: Docker image URI for ws_send_message Lambda.
        py_artifacts_dir: Path to Python Lambda zip bundles.
        log_retention: CloudWatch log retention in days.
        tavily_api_key: Tavily API key for web search.
    """

    def __init__(
        self,
        prefix: str,
        stack: str,
        *,
        conversations_table_name: pulumi.Output[str],
        conversations_table_arn: pulumi.Output[str],
        connections_table_name: pulumi.Output[str],
        connections_table_arn: pulumi.Output[str],
        reports_bucket_name: pulumi.Output[str],
        reports_bucket_arn: pulumi.Output[str],
        ws_management_endpoint: pulumi.Output[str],
        appconfig_app_id: pulumi.Output[str],
        appconfig_env_id: pulumi.Output[str],
        appconfig_profile_id: pulumi.Output[str],
        ecr_image_uri: pulumi.Output[str],
        py_artifacts_dir: str,
        log_retention: int,
        tavily_api_key: str = "",
    ):
        # ── ws_lifecycle (connect + disconnect, zip-based) ─────────────────
        lifecycle_env = {
            "CONNECTIONS_TABLE": connections_table_name,
        }
        self.ws_lifecycle = self._zip_lambda(
            prefix, stack,
            name="chat-ws-lifecycle",
            handler_name="ws_lifecycle",
            py_artifacts_dir=py_artifacts_dir,
            env=lifecycle_env,
            table_arns=[connections_table_arn],
            log_retention=log_retention,
            timeout=10,
        )

        # ── ws_send_message (Docker, Strands SDK) ──────────────────────────
        send_msg_role = aws.iam.Role(
            f"{prefix}-{stack}-chat-ws-send-msg-role",
            assume_role_policy=_trust_policy(),
        )

        send_msg_policy = pulumi.Output.all(
            conversations_table_arn,
            connections_table_arn,
            reports_bucket_arn,
        ).apply(lambda args: json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:GetItem", "dynamodb:PutItem",
                        "dynamodb:UpdateItem", "dynamodb:Query",
                    ],
                    "Resource": [args[0], args[1]],
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:PutObject", "s3:GetObject"],
                    "Resource": f"{args[2]}/*",
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream",
                    ],
                    "Resource": "arn:aws:bedrock:*::foundation-model/*",
                },
                {
                    "Effect": "Allow",
                    "Action": ["execute-api:ManageConnections"],
                    "Resource": "*",
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "appconfig:GetLatestConfiguration",
                        "appconfig:StartConfigurationSession",
                    ],
                    "Resource": "*",
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                    ],
                    "Resource": "*",
                },
                {
                    "Effect": "Allow",
                    "Action": ["xray:PutTraceSegments", "xray:PutTelemetryRecords"],
                    "Resource": "*",
                },
            ],
        }))

        aws.iam.RolePolicy(
            f"{prefix}-{stack}-chat-ws-send-msg-policy",
            role=send_msg_role.id,
            policy=send_msg_policy,
        )

        send_msg_env = {
            "CONVERSATIONS_TABLE": conversations_table_name,
            "CONNECTIONS_TABLE": connections_table_name,
            "REPORTS_BUCKET": reports_bucket_name,
            "WEBSOCKET_ENDPOINT": ws_management_endpoint,
            "APPCONFIG_APP": appconfig_app_id,
            "APPCONFIG_ENV": appconfig_env_id,
            "APPCONFIG_PROFILE": appconfig_profile_id,
            "TAVILY_API_KEY": tavily_api_key,
        }

        # AppConfig Lambda extension layer ARN (AWS-managed)
        appconfig_layer_arn = f"arn:aws:lambda:{aws.config.region}:080313899530:layer:AWS-AppConfig-Extension-Arm64:100"

        self.ws_send_message = aws.lambda_.Function(
            f"{prefix}-{stack}-chat-ws-send-msg",
            name=f"{prefix}-{stack}-chat-ws-send-msg",
            package_type="Image",
            image_uri=ecr_image_uri,
            architectures=["arm64"],
            role=send_msg_role.arn,
            timeout=120,
            memory_size=1024,
            environment=aws.lambda_.FunctionEnvironmentArgs(variables=send_msg_env),
            tracing_config=aws.lambda_.FunctionTracingConfigArgs(mode="Active"),
            layers=[appconfig_layer_arn],
        )

        aws.cloudwatch.LogGroup(
            f"{prefix}-{stack}-chat-ws-send-msg-logs",
            name=pulumi.Output.concat("/aws/lambda/", self.ws_send_message.name),
            retention_in_days=log_retention,
        )

        # ── research_chat_appsync (get + list conversations, zip-based) ────
        chat_appsync_env = {
            "CONVERSATIONS_TABLE": conversations_table_name,
        }
        self.research_chat_appsync = self._zip_lambda(
            prefix, stack,
            name="chat-appsync",
            handler_name="research_chat_appsync",
            py_artifacts_dir=py_artifacts_dir,
            env=chat_appsync_env,
            table_arns=[conversations_table_arn],
            log_retention=log_retention,
            timeout=10,
        )

    def _zip_lambda(
        self,
        prefix: str,
        stack: str,
        *,
        name: str,
        handler_name: str,
        py_artifacts_dir: str,
        env: dict,
        table_arns: list,
        log_retention: int,
        timeout: int = 10,
    ) -> aws.lambda_.Function:
        role = aws.iam.Role(
            f"{prefix}-{stack}-{name}-role",
            assume_role_policy=_trust_policy(),
        )

        policy = pulumi.Output.all(*table_arns).apply(lambda arns: json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:GetItem", "dynamodb:PutItem",
                        "dynamodb:UpdateItem", "dynamodb:DeleteItem",
                        "dynamodb:Query",
                    ],
                    "Resource": list(arns),
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                    ],
                    "Resource": "*",
                },
            ],
        }))

        aws.iam.RolePolicy(
            f"{prefix}-{stack}-{name}-policy",
            role=role.id,
            policy=policy,
        )

        pkg_dir = os.path.join(py_artifacts_dir, handler_name)
        fn = aws.lambda_.Function(
            f"{prefix}-{stack}-{name}",
            name=f"{prefix}-{stack}-{name}",
            runtime="python3.12",
            handler="handler.handler",
            architectures=["arm64"],
            role=role.arn,
            code=pulumi.FileArchive(pkg_dir),
            timeout=timeout,
            memory_size=256,
            environment=aws.lambda_.FunctionEnvironmentArgs(variables=env),
        )

        aws.cloudwatch.LogGroup(
            f"{prefix}-{stack}-{name}-logs",
            name=pulumi.Output.concat("/aws/lambda/", fn.name),
            retention_in_days=log_retention,
        )

        return fn
