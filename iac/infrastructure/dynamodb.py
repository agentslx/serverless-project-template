"""DynamoDB tables — long-lived, kept on resource policies (Retain on prod)."""
from __future__ import annotations

import pulumi
import pulumi_aws as aws


class UserProfileTable:
    """`user_profiles` — PK = user_id (Cognito sub)."""

    def __init__(self, prefix: str, stack: str):
        name = f"{prefix}-{stack}-user-profiles"
        self.table = aws.dynamodb.Table(
            f"{prefix}-{stack}-user-profiles",
            name=name,
            billing_mode="PAY_PER_REQUEST",
            hash_key="user_id",
            attributes=[aws.dynamodb.TableAttributeArgs(name="user_id", type="S")],
            point_in_time_recovery=aws.dynamodb.TablePointInTimeRecoveryArgs(
                enabled=stack == "prod"
            ),
            tags={"app": prefix, "stack": stack},
            opts=pulumi.ResourceOptions(
                # Protect prod from accidental deletes.
                protect=stack == "prod",
            ),
        )

    @property
    def name(self) -> pulumi.Output[str]:
        return self.table.name

    @property
    def arn(self) -> pulumi.Output[str]:
        return self.table.arn
