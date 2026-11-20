"""Amazon EventBridge rules for scheduled automations.

Provides serverless cron scheduling to trigger Step Functions or Lambda
on recurring intervals. Supports Track B scheduled workflow executions.
"""
from __future__ import annotations

import json
import pulumi
import pulumi_aws as aws


def _eventbridge_trust_policy() -> str:
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "events.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }],
    })


class ScheduledRule:
    """An EventBridge rule that triggers a target on a cron schedule.

    Args:
        prefix: Project prefix for naming.
        stack: Stack name (dev/prod).
        name: Logical rule name (e.g. "daily-reconciliation").
        schedule_expression: Cron or rate expression
            (e.g. "rate(1 hour)", "cron(0 9 * * ? *)").
        target_arn: ARN of the target (Step Functions or Lambda).
        target_role_arn: IAM role ARN EventBridge assumes to invoke the target.
    """

    def __init__(
        self,
        prefix: str,
        stack: str,
        *,
        name: str,
        schedule_expression: str,
        target_arn: pulumi.Output[str],
        target_role_arn: pulumi.Output[str],
    ):
        rule_name = f"{prefix}-{stack}-{name}"

        self.rule = aws.cloudwatch.EventRule(
            rule_name,
            name=rule_name,
            schedule_expression=schedule_expression,
            tags={"app": prefix, "stack": stack},
        )

        aws.cloudwatch.EventTarget(
            f"{rule_name}-target",
            rule=self.rule.name,
            arn=target_arn,
            role_arn=target_role_arn,
        )

    @property
    def arn(self) -> pulumi.Output[str]:
        return self.rule.arn
