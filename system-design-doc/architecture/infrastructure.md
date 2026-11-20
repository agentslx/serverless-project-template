# Infrastructure inventory

Pulumi creates the resources below. Names use `{project}-{stack}-{resource}` (e.g. `emergent-serverless-template-dev-users`).

## Long-lived (in `iac/infrastructure/`)

| Resource                | Module                       | Notes                                    |
|-------------------------|------------------------------|------------------------------------------|
| DynamoDB `user_profiles`| `infrastructure/dynamodb.py` | PK = `user_id` (S). PAY_PER_REQUEST.      |
| Cognito user pool       | `infrastructure/cognito.py`  | self sign-up ON, email verification       |
| Cognito admin pool      | `infrastructure/cognito.py`  | admin-create only, MFA optional           |
| AppSync API             | `infrastructure/appsync.py`  | Cognito auth (user pool), schema attached |
| AppSync data source     | `infrastructure/appsync.py`  | DynamoDB direct                          |
| S3 FE bucket            | `infrastructure/frontend_hosting.py` | private, OAC                     |
| CloudFront distribution | `infrastructure/frontend_hosting.py` | OAC, SPA fallback to /index.html |
| (optional) VPC + peering| `infrastructure/networking.py` | VPC, private subnets, peering, internal DNS |
| (optional) SQS + DLQ   | `infrastructure/sqs.py`        | event-driven decoupling, retry via redrive |
| (optional) SNS topics   | `infrastructure/sns.py`        | async pub/sub between processing phases  |
| (optional) Step Functions| `infrastructure/step_functions.py` | workflow orchestration state machines |
| (optional) API Gateway  | `infrastructure/api_gateway.py`| REST API with async 202 pattern          |
| (optional) EventBridge  | `infrastructure/eventbridge.py`| scheduled cron rules for automations     |
| (optional) S3 processing| `infrastructure/s3_processing.py` | lifecycle policies, tier transitions  |
| DynamoDB `conversations`| `infrastructure/dynamodb_conversations.py` | PK=user_id, SK=conversation_id  |
| DynamoDB `ws-connections`| `infrastructure/dynamodb_conversations.py` | PK=connection_id, TTL-based     |
| WebSocket API Gateway   | `infrastructure/websocket_api.py` | chat streaming, route selection on action |
| AppConfig (chat-agent)  | `infrastructure/appconfig.py` | dynamic model config, no-redeploy changes |
| S3 `chat-reports`       | `infrastructure/s3_processing.py` | markdown reports, 90d expiration     |

## Application (in `iac/application/`)

| Resource             | Module                    | Notes                                   |
|----------------------|---------------------------|-----------------------------------------|
| Lambda functions     | `application/lambdas.py`  | one per feature per protocol (consolidated) |
| Lambda IAM roles     | `application/lambdas.py`  | least-privilege per fn                  |
| Chat Lambdas         | `application/chat_lambdas.py` | ws_lifecycle, ws_send_message (Docker), research_chat_appsync |
| AppSync resolvers    | `application/lambdas.py`  | wires JS resolvers + lambda data sources |
| FE bundle upload     | `application/frontend.py` | syncs `frontend/build/` → S3            |
| CloudFront invalid.  | `application/frontend.py` | runs after upload                       |

## IAM principles

- One IAM role **per** Lambda. No "lambda-everything" role.
- Use Pulumi `aws.iam.RolePolicy` with the minimum action set (`dynamodb:GetItem`, etc.).
- AppSync direct DynamoDB has its own service role.
