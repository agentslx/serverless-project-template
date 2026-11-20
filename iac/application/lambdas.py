"""Lambda functions — one per binary built by `cargo lambda build --workspace`
or per Python handler bundled by `scripts/package_py_lambdas.sh`.

Per AGENTS.md §6 each function has its own least-privilege IAM role.
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


def _ddb_policy(table_arn) -> pulumi.Output[str]:
    return pulumi.Output.from_input(table_arn).apply(lambda a: json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem", "dynamodb:PutItem",
                    "dynamodb:UpdateItem", "dynamodb:Query", "dynamodb:Scan",
                ],
                "Resource": a,
            },
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
        ],
    }))


class _RustLambda:
    """One Rust Lambda function with its own role + log group.

    `bin_dir` should point at the directory `cargo lambda build` emits, i.e.
    `backend/target/lambda/<bin_name>/` (containing `bootstrap`).
    """

    def __init__(self, prefix: str, stack: str, *, name: str, bin_dir: str,
                 env: dict, table_arn, log_retention: int):
        role = aws.iam.Role(
            f"{prefix}-{stack}-{name}-role",
            assume_role_policy=_trust_policy(),
        )
        aws.iam.RolePolicy(
            f"{prefix}-{stack}-{name}-policy",
            role=role.id,
            policy=_ddb_policy(table_arn),
        )

        self.fn = aws.lambda_.Function(
            f"{prefix}-{stack}-{name}",
            name=f"{prefix}-{stack}-{name}",
            runtime="provided.al2023",
            handler="bootstrap",
            architectures=["arm64"],
            role=role.arn,
            code=pulumi.FileArchive(bin_dir),
            timeout=10,
            memory_size=256,
            environment=aws.lambda_.FunctionEnvironmentArgs(variables=env),
            tracing_config=aws.lambda_.FunctionTracingConfigArgs(mode="Active"),
        )

        aws.cloudwatch.LogGroup(
            f"{prefix}-{stack}-{name}-logs",
            name=pulumi.Output.concat("/aws/lambda/", self.fn.name),
            retention_in_days=log_retention,
        )

    @property
    def arn(self):
        return self.fn.arn


class _PythonLambda:
    """One Python Lambda function with its own role + log group.

    `pkg_dir` should point at a directory bundled by
    `scripts/package_py_lambdas.sh`, i.e.
    `backend/target/python_lambda/<handler_name>/` (containing `handler.py`
    + the relative `feature/` and `shared/` packages).
    """

    def __init__(self, prefix: str, stack: str, *, name: str, pkg_dir: str,
                 env: dict, table_arn, log_retention: int,
                 handler: str = "handler.handler"):
        role = aws.iam.Role(
            f"{prefix}-{stack}-{name}-role",
            assume_role_policy=_trust_policy(),
        )
        aws.iam.RolePolicy(
            f"{prefix}-{stack}-{name}-policy",
            role=role.id,
            policy=_ddb_policy(table_arn),
        )

        self.fn = aws.lambda_.Function(
            f"{prefix}-{stack}-{name}",
            name=f"{prefix}-{stack}-{name}",
            runtime="python3.12",
            handler=handler,
            architectures=["arm64"],
            role=role.arn,
            code=pulumi.FileArchive(pkg_dir),
            timeout=10,
            memory_size=256,
            environment=aws.lambda_.FunctionEnvironmentArgs(variables=env),
        )

        aws.cloudwatch.LogGroup(
            f"{prefix}-{stack}-{name}-logs",
            name=pulumi.Output.concat("/aws/lambda/", self.fn.name),
            retention_in_days=log_retention,
        )

    @property
    def arn(self):
        return self.fn.arn


class Lambdas:
    """Wires every Lambda binary defined under
    `backend/feature/*_rs/presentation/lambda_handlers/*` (Rust) and every
    handler under `backend/feature/*_py/presentation/lambda_handlers/*`
    (Python).

    Pulumi config keys:
      - `lambdaArtifactsDir`        Rust artefacts (cargo-lambda output).
      - `pythonLambdaArtifactsDir`  Python bundles. Optional — if missing,
                                    no Python Lambdas are deployed (the
                                    Rust crates remain the canonical path).
      - `logRetentionDays`
    """

    def __init__(self, prefix: str, stack: str, *, table, pools, cfg: pulumi.Config):
        artefacts = cfg.require("lambdaArtifactsDir")
        py_artefacts = cfg.get("pythonLambdaArtifactsDir")  # optional
        log_retention = int(cfg.require("logRetentionDays"))

        common_env = {
            "USER_PROFILES_TABLE": table.name,
            "AWS_REGION": aws.config.region,
            "LOG_LEVEL": "info",
        }

        # ── Rust lambdas (canonical) ────────────────────────────────────
        self.get_me = _RustLambda(
            prefix, stack,
            name="handler-get-me",
            bin_dir=os.path.join(artefacts, "handler_get_me"),
            env=common_env, table_arn=table.arn, log_retention=log_retention,
        )

        self.post_confirmation = _RustLambda(
            prefix, stack,
            name="handler-post-confirmation",
            bin_dir=os.path.join(artefacts, "handler_post_confirmation_trigger"),
            env=common_env, table_arn=table.arn, log_retention=log_retention,
        )

        self.user_profile = _RustLambda(
            prefix, stack,
            name="handler-user-profile",
            bin_dir=os.path.join(artefacts, "handler_user_profile"),
            env=common_env, table_arn=table.arn, log_retention=log_retention,
        )

        self.list_users = _RustLambda(
            prefix, stack,
            name="handler-list-users",
            bin_dir=os.path.join(artefacts, "handler_list_users"),
            env=common_env, table_arn=table.arn, log_retention=log_retention,
        )

        # ── Python lambdas (parity, optional) ───────────────────────────
        # Deployed only when `pythonLambdaArtifactsDir` is configured AND the
        # handler bundle exists. Mirrors the Rust set 1-for-1; pick whichever
        # language a real project standardises on.
        self.python: dict[str, _PythonLambda] = {}
        if py_artefacts:
            for handler_name in (
                "get_me",
                "user_profile_handler",
                "post_confirmation_trigger",
                "health",
            ):
                pkg = os.path.join(py_artefacts, handler_name)
                if not os.path.isdir(pkg):
                    pulumi.log.info(
                        f"python lambda {handler_name!r} skipped — bundle not found "
                        f"at {pkg} (run scripts/package_py_lambdas.sh first)."
                    )
                    continue
                self.python[handler_name] = _PythonLambda(
                    prefix, stack,
                    name=f"py-handler-{handler_name.replace('_', '-')}",
                    pkg_dir=pkg,
                    env=common_env,
                    table_arn=table.arn,
                    log_retention=log_retention,
                )

        # ── Permissions ─────────────────────────────────────────────────
        # Allow Cognito to invoke the post-confirmation trigger.
        aws.lambda_.Permission(
            f"{prefix}-{stack}-cognito-invoke",
            action="lambda:InvokeFunction",
            function=self.post_confirmation.fn.name,
            principal="cognito-idp.amazonaws.com",
            source_arn=pools.user_pool.arn,
        )

        # Allow AppSync (user API) to invoke the user_profile lambda.
        aws.lambda_.Permission(
            f"{prefix}-{stack}-appsync-invoke",
            action="lambda:InvokeFunction",
            function=self.user_profile.fn.name,
            principal="appsync.amazonaws.com",
        )

        # Allow AppSync (admin API) to invoke the list_users lambda.
        aws.lambda_.Permission(
            f"{prefix}-{stack}-appsync-admin-invoke",
            action="lambda:InvokeFunction",
            function=self.list_users.fn.name,
            principal="appsync.amazonaws.com",
        )
