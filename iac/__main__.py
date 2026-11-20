"""Thin orchestrator. Wires modules from `infrastructure/` and `application/`.

Per AGENTS.md §6 this file MUST stay tiny.
"""
from __future__ import annotations

import pulumi

from infrastructure.dynamodb import UserProfileTable
from infrastructure.cognito import CognitoPools
from infrastructure.appsync import AppSyncApi
from infrastructure.appsync_admin import AdminAppSyncApi
from infrastructure.frontend_hosting import FrontendHosting
from application.lambdas import Lambdas
from application.frontend import FrontendBundle

# ── Chat feature ───────────────────────────────────────────────────────
from infrastructure.dynamodb_conversations import ConversationsTable, ConnectionsTable
from infrastructure.appconfig import AppConfigSetup
from infrastructure.websocket_api import ChatWebSocketApi
from infrastructure.s3_processing import ProcessingBucket
from application.chat_lambdas import ChatLambdas

# ── Optional modules (uncomment when needed) ───────────────────────────
# from infrastructure.sqs import SqsQueue
# from infrastructure.sns import SnsTopic
# from infrastructure.step_functions import StepFunctionStateMachine
# from infrastructure.api_gateway import RestApiAsync
# from infrastructure.eventbridge import ScheduledRule
# from infrastructure.networking import Networking

cfg = pulumi.Config()
prefix = cfg.require("projectPrefix")
stack = cfg.require("stackName")

# 1. Long-lived infrastructure
table = UserProfileTable(prefix, stack)
pools = CognitoPools(prefix, stack)
user_host  = FrontendHosting(prefix, stack, app_name="user")
admin_host = FrontendHosting(prefix, stack, app_name="admin")

# 2. Application — Lambdas
lambdas = Lambdas(prefix, stack, table=table, pools=pools, cfg=cfg)

# 3. AppSync API
api = AppSyncApi(
    prefix, stack,
    table=table, pools=pools,
    user_profile_lambda_arn=lambdas.user_profile.arn,
)

# 3b. Admin AppSync API (separate API, admin pool, list_users only)
admin_api = AdminAppSyncApi(
    prefix, stack,
    pools=pools,
    list_users_lambda_arn=lambdas.list_users.arn,
)

# 4. Frontend bundles + invalidation
FrontendBundle(prefix, stack,
               hosting=user_host,
               bundle_dir=cfg.require("userFrontendBundleDir"),
               app_name="user")
FrontendBundle(prefix, stack,
               hosting=admin_host,
               bundle_dir=cfg.require("adminFrontendBundleDir"),
               app_name="admin")

# 5. Chat feature — Research Agent Team
conversations_table = ConversationsTable(prefix, stack)
connections_table = ConnectionsTable(prefix, stack)
appconfig = AppConfigSetup(prefix, stack)
reports_bucket = ProcessingBucket(prefix, stack, name="chat-reports", expiration_days=90)

chat_lambdas = ChatLambdas(
    prefix, stack,
    conversations_table_name=conversations_table.name,
    conversations_table_arn=conversations_table.arn,
    connections_table_name=connections_table.name,
    connections_table_arn=connections_table.arn,
    reports_bucket_name=reports_bucket.name,
    reports_bucket_arn=reports_bucket.arn,
    ws_management_endpoint=pulumi.Output.from_input(""),  # set after WS API created
    appconfig_app_id=appconfig.app_id,
    appconfig_env_id=appconfig.env_id,
    appconfig_profile_id=appconfig.profile_id,
    ecr_image_uri=cfg.require("chatLambdaImageUri"),
    py_artifacts_dir=cfg.get("pythonLambdaArtifactsDir") or "../backend/target/python_lambda",
    log_retention=int(cfg.require("logRetentionDays")),
    tavily_api_key=cfg.get_secret("tavilyApiKey") or "",
)

ws_api = ChatWebSocketApi(
    prefix, stack,
    connect_fn_arn=chat_lambdas.ws_lifecycle.arn,
    disconnect_fn_arn=chat_lambdas.ws_lifecycle.arn,
    send_message_fn_arn=chat_lambdas.ws_send_message.arn,
    connect_fn_name=chat_lambdas.ws_lifecycle.name,
    disconnect_fn_name=chat_lambdas.ws_lifecycle.name,
    send_message_fn_name=chat_lambdas.ws_send_message.name,
)

# 6. Outputs
pulumi.export("region", "ap-southeast-2")
pulumi.export("user_profiles_table", table.name)
pulumi.export("user_pool_id", pools.user_pool.id)
pulumi.export("user_pool_client_id", pools.user_pool_client.id)
pulumi.export("admin_pool_id", pools.admin_pool.id)
pulumi.export("admin_pool_client_id", pools.admin_pool_client.id)
pulumi.export("appsync_url", api.api.uris["GRAPHQL"])
pulumi.export("admin_appsync_url", admin_api.api.uris["GRAPHQL"])
pulumi.export("user_frontend_url",
              user_host.cdn.domain_name.apply(lambda d: f"https://{d}"))
pulumi.export("admin_frontend_url",
              admin_host.cdn.domain_name.apply(lambda d: f"https://{d}"))
pulumi.export("chat_ws_url", ws_api.ws_url)
pulumi.export("conversations_table", conversations_table.name)
pulumi.export("chat_reports_bucket", reports_bucket.name)

# ── Optional infrastructure (uncomment and configure as needed) ─────────
#
# # Event-driven processing pipeline
# ocr_queue = SqsQueue(prefix, stack, name="ocr-tasks", visibility_timeout=120)
# extraction_queue = SqsQueue(prefix, stack, name="extraction", visibility_timeout=60)
# textract_complete_topic = SnsTopic(prefix, stack, name="textract-complete")
# textract_complete_topic.subscribe_sqs(extraction_queue.arn, "extraction")
#
# # Processing buckets with lifecycle policies
# raw_docs = ProcessingBucket(prefix, stack, name="raw-documents")
# ai_output = ProcessingBucket(prefix, stack, name="ai-output", ia_transition_days=14)
#
# # Step Functions workflow orchestration
# triage_sm = StepFunctionStateMachine(
#     prefix, stack,
#     name="triage",
#     definition={
#         "Comment": "Application triage state machine",
#         "StartAt": "Validate",
#         "States": {
#             "Validate": {"Type": "Pass", "End": True},
#         },
#     },
#     iam_statements=[{
#         "Effect": "Allow",
#         "Action": ["lambda:InvokeFunction"],
#         "Resource": "*",
#     }],
#     timeout_seconds=900,
# )
#
# # Async REST API (returns 202, triggers Step Functions)
# workflow_api = RestApiAsync(
#     prefix, stack,
#     name="workflow-trigger",
#     step_function_arn=triage_sm.arn,
# )
#
# # Scheduled automation via EventBridge
# daily_rule = ScheduledRule(
#     prefix, stack,
#     name="daily-reconciliation",
#     schedule_expression="cron(0 9 * * ? *)",
#     target_arn=triage_sm.arn,
#     target_role_arn=triage_sm.role.arn,
# )
#
# # VPC + peering (for internal DNS resolution / RDS access)
# network = Networking(
#     prefix, stack,
#     peer_vpc_id="vpc-xxxxxxxx",
#     peer_vpc_cidr="172.16.0.0/16",
# )
#
# # Additional outputs
# pulumi.export("ocr_queue_url", ocr_queue.url)
# pulumi.export("workflow_api_url", workflow_api.invoke_url)
# pulumi.export("raw_docs_bucket", raw_docs.name)
