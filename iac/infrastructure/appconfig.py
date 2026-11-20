"""AWS AppConfig for dynamic agent configuration (model, temperature, etc.).

Allows changing agent behavior without redeploying Lambdas.
"""
from __future__ import annotations

import json
import pulumi
import pulumi_aws as aws


class AppConfigSetup:
    """AppConfig application with a chat-agent configuration profile.

    The Lambda reads config via the AppConfig Lambda extension at runtime
    (http://localhost:2772/...) with built-in caching.
    """

    def __init__(self, prefix: str, stack: str):
        app_name = f"{prefix}-{stack}"

        self.app = aws.appconfig.Application(
            f"{app_name}-appconfig",
            name=app_name,
            tags={"app": prefix, "stack": stack},
        )

        self.env = aws.appconfig.Environment(
            f"{app_name}-appconfig-env",
            application_id=self.app.id,
            name=stack,
            tags={"app": prefix, "stack": stack},
        )

        self.profile = aws.appconfig.ConfigurationProfile(
            f"{app_name}-chat-config",
            application_id=self.app.id,
            name="chat-agent-config",
            location_uri="hosted",
            tags={"app": prefix, "stack": stack},
        )

        default_config = {
            "model_id": "global.anthropic.claude-sonnet-4-6",
            "max_tokens": 4096,
            "temperature": 0.3,
        }

        self.config_version = aws.appconfig.HostedConfigurationVersion(
            f"{app_name}-chat-config-v1",
            application_id=self.app.id,
            configuration_profile_id=self.profile.configuration_profile_id,
            content_type="application/json",
            content=json.dumps(default_config),
        )

        self.strategy = aws.appconfig.DeploymentStrategy(
            f"{app_name}-instant-deploy",
            name=f"{app_name}-instant",
            deployment_duration_in_minutes=0,
            growth_factor=100,
            replicate_to="NONE",
            final_bake_time_in_minutes=0,
            tags={"app": prefix, "stack": stack},
        )

        self.deployment = aws.appconfig.Deployment(
            f"{app_name}-chat-config-deploy",
            application_id=self.app.id,
            environment_id=self.env.environment_id,
            configuration_profile_id=self.profile.configuration_profile_id,
            configuration_version=self.config_version.version_number.apply(str),
            deployment_strategy_id=self.strategy.id,
        )

    @property
    def app_id(self) -> pulumi.Output[str]:
        return self.app.id

    @property
    def env_id(self) -> pulumi.Output[str]:
        return self.env.environment_id

    @property
    def profile_id(self) -> pulumi.Output[str]:
        return self.profile.configuration_profile_id
