"""Cognito user pool + admin pool.

- User pool: self sign-up + email verification.
- Admin pool: admin-create only, no public sign-up.
"""
from __future__ import annotations

import pulumi
import pulumi_aws as aws


class CognitoPools:
    def __init__(self, prefix: str, stack: str):
        # ---- USER pool ----
        self.user_pool = aws.cognito.UserPool(
            f"{prefix}-{stack}-user-pool",
            name=f"{prefix}-{stack}-user-pool",
            alias_attributes=["email"],
            auto_verified_attributes=["email"],
            password_policy=aws.cognito.UserPoolPasswordPolicyArgs(
                minimum_length=8,
                require_lowercase=True,
                require_numbers=True,
                require_symbols=False,
                require_uppercase=True,
            ),
            schemas=[
                aws.cognito.UserPoolSchemaArgs(
                    name="email",
                    attribute_data_type="String",
                    required=True,
                    mutable=True,
                )
            ],
            account_recovery_setting=aws.cognito.UserPoolAccountRecoverySettingArgs(
                recovery_mechanisms=[
                    aws.cognito.UserPoolAccountRecoverySettingRecoveryMechanismArgs(
                        name="verified_email", priority=1
                    )
                ]
            ),
            tags={"app": prefix, "stack": stack},
        )
        self.user_pool_client = aws.cognito.UserPoolClient(
            f"{prefix}-{stack}-user-pool-client",
            user_pool_id=self.user_pool.id,
            generate_secret=False,
            explicit_auth_flows=[
                "ALLOW_USER_SRP_AUTH",
                "ALLOW_USER_PASSWORD_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
            ],
            prevent_user_existence_errors="ENABLED",
        )

        # ---- ADMIN pool ----
        self.admin_pool = aws.cognito.UserPool(
            f"{prefix}-{stack}-admin-pool",
            name=f"{prefix}-{stack}-admin-pool",
            alias_attributes=["email"],
            admin_create_user_config=aws.cognito.UserPoolAdminCreateUserConfigArgs(
                allow_admin_create_user_only=True,
            ),
            auto_verified_attributes=["email"],
            password_policy=aws.cognito.UserPoolPasswordPolicyArgs(
                minimum_length=12,
                require_lowercase=True,
                require_numbers=True,
                require_symbols=True,
                require_uppercase=True,
            ),
            mfa_configuration="OPTIONAL",
            software_token_mfa_configuration=aws.cognito.UserPoolSoftwareTokenMfaConfigurationArgs(
                enabled=True,
            ),
            tags={"app": prefix, "stack": stack},
        )
        self.admin_pool_client = aws.cognito.UserPoolClient(
            f"{prefix}-{stack}-admin-pool-client",
            user_pool_id=self.admin_pool.id,
            generate_secret=False,
            explicit_auth_flows=["ALLOW_USER_SRP_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"],
            prevent_user_existence_errors="ENABLED",
        )

    def attach_post_confirmation_trigger(self, lambda_arn: pulumi.Output[str]):
        """Wire the `post_confirmation_trigger` Lambda after Lambdas module created it."""
        return aws.cognito.UserPool(
            f"{self.user_pool._name}-trigger-update",
            user_pool_id=self.user_pool.id,
            lambda_config=aws.cognito.UserPoolLambdaConfigArgs(
                post_confirmation=lambda_arn,
            ),
            opts=pulumi.ResourceOptions(import_=self.user_pool.id),
        )
