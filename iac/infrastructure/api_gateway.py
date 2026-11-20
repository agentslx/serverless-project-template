"""Amazon API Gateway (REST) with async 202 Accepted integration pattern.

Provides a REST API that returns 202 immediately while Step Functions
processes long-running workflows in the background. Suitable for AI
pipelines where synchronous responses would exceed gateway timeouts.
"""
from __future__ import annotations

import json
import pulumi
import pulumi_aws as aws


def _apigw_trust_policy() -> str:
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "apigateway.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }],
    })


class RestApiAsync:
    """A REST API Gateway with direct Step Functions integration (async pattern).

    Args:
        prefix: Project prefix for naming.
        stack: Stack name (dev/prod).
        name: Logical API name (e.g. "workflow-trigger").
        step_function_arn: ARN of the Step Functions state machine to invoke.
        stage_name: Deployment stage (default "v1").
    """

    def __init__(
        self,
        prefix: str,
        stack: str,
        *,
        name: str,
        step_function_arn: pulumi.Output[str],
        stage_name: str = "v1",
    ):
        api_name = f"{prefix}-{stack}-{name}"

        self.api = aws.apigateway.RestApi(
            api_name,
            name=api_name,
            description=f"Async REST API for {name}",
            tags={"app": prefix, "stack": stack},
        )

        self.role = aws.iam.Role(
            f"{api_name}-role",
            assume_role_policy=_apigw_trust_policy(),
            tags={"app": prefix, "stack": stack},
        )

        aws.iam.RolePolicy(
            f"{api_name}-sfn-policy",
            role=self.role.id,
            policy=step_function_arn.apply(lambda arn: json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": "states:StartExecution",
                    "Resource": arn,
                }],
            })),
        )

        resource = aws.apigateway.Resource(
            f"{api_name}-resource",
            rest_api=self.api.id,
            parent_id=self.api.root_resource_id,
            path_part="execute",
        )

        aws.apigateway.Method(
            f"{api_name}-method",
            rest_api=self.api.id,
            resource_id=resource.id,
            http_method="POST",
            authorization="IAM",
        )

        aws.apigateway.Integration(
            f"{api_name}-integration",
            rest_api=self.api.id,
            resource_id=resource.id,
            http_method="POST",
            integration_http_method="POST",
            type="AWS",
            uri=pulumi.Output.concat(
                "arn:aws:apigateway:",
                aws.config.region or "ap-southeast-2",
                ":states:action/StartExecution",
            ),
            credentials=self.role.arn,
            request_templates={
                "application/json": step_function_arn.apply(
                    lambda arn: json.dumps({
                        "input": "$util.escapeJavaScript($input.body)",
                        "stateMachineArn": arn,
                    })
                ),
            },
        )

        aws.apigateway.MethodResponse(
            f"{api_name}-response-202",
            rest_api=self.api.id,
            resource_id=resource.id,
            http_method="POST",
            status_code="202",
        )

        aws.apigateway.IntegrationResponse(
            f"{api_name}-int-response-202",
            rest_api=self.api.id,
            resource_id=resource.id,
            http_method="POST",
            status_code="202",
            response_templates={"application/json": '{"status": "accepted"}'},
        )

        self.deployment = aws.apigateway.Deployment(
            f"{api_name}-deployment",
            rest_api=self.api.id,
            stage_name=stage_name,
        )

    @property
    def invoke_url(self) -> pulumi.Output[str]:
        return self.deployment.invoke_url
