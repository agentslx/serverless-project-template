"""API Gateway WebSocket API for real-time chat streaming."""
from __future__ import annotations

import json
import pulumi
import pulumi_aws as aws


class ChatWebSocketApi:
    """WebSocket API with $connect, $disconnect, and sendMessage routes.

    Each route is backed by a separate Lambda function.
    """

    def __init__(
        self,
        prefix: str,
        stack: str,
        *,
        connect_fn_arn: pulumi.Output[str],
        disconnect_fn_arn: pulumi.Output[str],
        send_message_fn_arn: pulumi.Output[str],
        connect_fn_name: pulumi.Output[str],
        disconnect_fn_name: pulumi.Output[str],
        send_message_fn_name: pulumi.Output[str],
    ):
        api_name = f"{prefix}-{stack}-chat-ws"

        self.api = aws.apigatewayv2.Api(
            api_name,
            name=api_name,
            protocol_type="WEBSOCKET",
            route_selection_expression="$request.body.action",
            tags={"app": prefix, "stack": stack},
        )

        # Integrations
        connect_integration = aws.apigatewayv2.Integration(
            f"{api_name}-connect-int",
            api_id=self.api.id,
            integration_type="AWS_PROXY",
            integration_uri=connect_fn_arn,
        )

        disconnect_integration = aws.apigatewayv2.Integration(
            f"{api_name}-disconnect-int",
            api_id=self.api.id,
            integration_type="AWS_PROXY",
            integration_uri=disconnect_fn_arn,
        )

        send_message_integration = aws.apigatewayv2.Integration(
            f"{api_name}-send-msg-int",
            api_id=self.api.id,
            integration_type="AWS_PROXY",
            integration_uri=send_message_fn_arn,
        )

        # Routes
        aws.apigatewayv2.Route(
            f"{api_name}-connect-route",
            api_id=self.api.id,
            route_key="$connect",
            target=connect_integration.id.apply(lambda id: f"integrations/{id}"),
        )

        aws.apigatewayv2.Route(
            f"{api_name}-disconnect-route",
            api_id=self.api.id,
            route_key="$disconnect",
            target=disconnect_integration.id.apply(lambda id: f"integrations/{id}"),
        )

        aws.apigatewayv2.Route(
            f"{api_name}-send-msg-route",
            api_id=self.api.id,
            route_key="sendMessage",
            target=send_message_integration.id.apply(lambda id: f"integrations/{id}"),
        )

        # Stage (auto-deploy)
        self.stage = aws.apigatewayv2.Stage(
            f"{api_name}-stage",
            api_id=self.api.id,
            name=stack,
            auto_deploy=True,
            tags={"app": prefix, "stack": stack},
        )

        # Lambda permissions for API Gateway to invoke
        aws.lambda_.Permission(
            f"{api_name}-lifecycle-perm",
            action="lambda:InvokeFunction",
            function=connect_fn_name,
            principal="apigateway.amazonaws.com",
            source_arn=self.api.execution_arn.apply(lambda arn: f"{arn}/*"),
        )

        aws.lambda_.Permission(
            f"{api_name}-send-msg-perm",
            action="lambda:InvokeFunction",
            function=send_message_fn_name,
            principal="apigateway.amazonaws.com",
            source_arn=self.api.execution_arn.apply(lambda arn: f"{arn}/*"),
        )

    @property
    def ws_url(self) -> pulumi.Output[str]:
        """The wss:// endpoint clients connect to."""
        return pulumi.Output.all(self.api.api_endpoint, self.stage.name).apply(
            lambda args: f"{args[0]}/{args[1]}"
        )

    @property
    def management_endpoint(self) -> pulumi.Output[str]:
        """HTTPS endpoint for @connections API (post_to_connection)."""
        return pulumi.Output.all(self.api.id, self.stage.name).apply(
            lambda args: f"https://{args[0]}.execute-api.{aws.config.region}.amazonaws.com/{args[1]}"
        )
