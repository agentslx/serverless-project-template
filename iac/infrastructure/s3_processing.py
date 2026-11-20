"""S3 processing buckets with lifecycle policies.

Provides document ingestion and output buckets with automatic tier
transitions (Standard → Infrequent Access → Glacier) to optimize
storage costs for raw documents, extracted text, and AI outputs.
"""
from __future__ import annotations

import pulumi
import pulumi_aws as aws


class ProcessingBucket:
    """An S3 bucket with lifecycle rules for document processing pipelines.

    Args:
        prefix: Project prefix for naming.
        stack: Stack name (dev/prod).
        name: Logical bucket purpose (e.g. "raw-documents", "ai-output").
        ia_transition_days: Days before transitioning to Infrequent Access.
        glacier_transition_days: Days before transitioning to Glacier.
        expiration_days: Days before permanent deletion (0 = never expire).
        versioning: Enable versioning (recommended for prod).
    """

    def __init__(
        self,
        prefix: str,
        stack: str,
        *,
        name: str,
        ia_transition_days: int = 30,
        glacier_transition_days: int = 90,
        expiration_days: int = 0,
        versioning: bool = False,
    ):
        bucket_name = f"{prefix}-{stack}-{name}"

        lifecycle_rules = [
            aws.s3.BucketLifecycleRuleArgs(
                id="tier-transition",
                enabled=True,
                transitions=[
                    aws.s3.BucketLifecycleRuleTransitionArgs(
                        days=ia_transition_days,
                        storage_class="STANDARD_IA",
                    ),
                    aws.s3.BucketLifecycleRuleTransitionArgs(
                        days=glacier_transition_days,
                        storage_class="GLACIER",
                    ),
                ],
                expiration=aws.s3.BucketLifecycleRuleExpirationArgs(
                    days=expiration_days,
                ) if expiration_days > 0 else None,
            ),
        ]

        self.bucket = aws.s3.Bucket(
            bucket_name,
            bucket=bucket_name,
            acl="private",
            versioning=aws.s3.BucketVersioningArgs(
                enabled=versioning or stack == "prod",
            ),
            lifecycle_rules=lifecycle_rules,
            server_side_encryption_configuration=aws.s3.BucketServerSideEncryptionConfigurationArgs(
                rule=aws.s3.BucketServerSideEncryptionConfigurationRuleArgs(
                    apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultArgs(
                        sse_algorithm="AES256",
                    ),
                ),
            ),
            tags={"app": prefix, "stack": stack},
            opts=pulumi.ResourceOptions(protect=stack == "prod"),
        )

        aws.s3.BucketPublicAccessBlock(
            f"{bucket_name}-block-public",
            bucket=self.bucket.id,
            block_public_acls=True,
            block_public_policy=True,
            ignore_public_acls=True,
            restrict_public_buckets=True,
        )

    @property
    def name(self) -> pulumi.Output[str]:
        return self.bucket.bucket

    @property
    def arn(self) -> pulumi.Output[str]:
        return self.bucket.arn

    @property
    def id(self) -> pulumi.Output[str]:
        return self.bucket.id
