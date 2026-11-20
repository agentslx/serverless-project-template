"""AWS Step Functions state machines for workflow orchestration.

Provides resilient macro-orchestration for multi-step business logic,
parallel Lambda executions, and long-running AI workflows with timeout
guardrails.
"""
from __future__ import annotations

import json
import pulumi
import pulumi_aws as aws


def _sfn_trust_policy() -> str:
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "states.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }],
    })


class StepFunctionStateMachine:
    """An AWS Step Functions state machine with its own IAM role.

    Args:
        prefix: Project prefix for naming.
        stack: Stack name (dev/prod).
        name: Logical state machine name (e.g. "triage", "expense-verify").
        definition: ASL definition as a Python dict (will be JSON-serialized).
        iam_statements: Additional IAM policy statements the state machine
            needs (e.g. lambda:InvokeFunction, bedrock:InvokeModel).
        timeout_seconds: Maximum execution time before forced abort.
    """

    def __init__(
        self,
        prefix: str,
        stack: str,
        *,
        name: str,
        definition: dict,
        iam_statements: list[dict] | None = None,
        timeout_seconds: int = 300,
    ):
        sm_name = f"{prefix}-{stack}-{name}"

        self.role = aws.iam.Role(
            f"{sm_name}-role",
            assume_role_policy=_sfn_trust_policy(),
            tags={"app": prefix, "stack": stack},
        )

        statements = [
            {
                "Effect": "Allow",
                "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                "Resource": "*",
            },
            {
                "Effect": "Allow",
                "Action": ["xray:PutTraceSegments", "xray:PutTelemetryRecords"],
                "Resource": "*",
            },
        ]
        if iam_statements:
            statements.extend(iam_statements)

        aws.iam.RolePolicy(
            f"{sm_name}-policy",
            role=self.role.id,
            policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": statements,
            }),
        )

        definition["TimeoutSeconds"] = timeout_seconds

        self.state_machine = aws.sfn.StateMachine(
            sm_name,
            name=sm_name,
            role_arn=self.role.arn,
            definition=json.dumps(definition),
            tracing_configuration=aws.sfn.StateMachineTracingConfigurationArgs(
                enabled=True,
            ),
            tags={"app": prefix, "stack": stack},
        )

    @property
    def arn(self) -> pulumi.Output[str]:
        return self.state_machine.arn
