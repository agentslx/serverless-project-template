"""DynamoDB table for chat conversations + WebSocket connections."""
from __future__ import annotations

import pulumi
import pulumi_aws as aws


class ConversationsTable:
    """Chat conversations — PK = user_id, SK = conversation_id."""

    def __init__(self, prefix: str, stack: str):
        name = f"{prefix}-{stack}-conversations"
        self.table = aws.dynamodb.Table(
            name,
            name=name,
            billing_mode="PAY_PER_REQUEST",
            hash_key="user_id",
            range_key="conversation_id",
            attributes=[
                aws.dynamodb.TableAttributeArgs(name="user_id", type="S"),
                aws.dynamodb.TableAttributeArgs(name="conversation_id", type="S"),
            ],
            point_in_time_recovery=aws.dynamodb.TablePointInTimeRecoveryArgs(
                enabled=stack == "prod"
            ),
            tags={"app": prefix, "stack": stack},
            opts=pulumi.ResourceOptions(protect=stack == "prod"),
        )

    @property
    def name(self) -> pulumi.Output[str]:
        return self.table.name

    @property
    def arn(self) -> pulumi.Output[str]:
        return self.table.arn


class ConnectionsTable:
    """WebSocket connections — PK = connection_id, TTL on `ttl` attribute."""

    def __init__(self, prefix: str, stack: str):
        name = f"{prefix}-{stack}-ws-connections"
        self.table = aws.dynamodb.Table(
            name,
            name=name,
            billing_mode="PAY_PER_REQUEST",
            hash_key="connection_id",
            attributes=[
                aws.dynamodb.TableAttributeArgs(name="connection_id", type="S"),
            ],
            ttl=aws.dynamodb.TableTtlArgs(
                attribute_name="ttl",
                enabled=True,
            ),
            tags={"app": prefix, "stack": stack},
        )

    @property
    def name(self) -> pulumi.Output[str]:
        return self.table.name

    @property
    def arn(self) -> pulumi.Output[str]:
        return self.table.arn
