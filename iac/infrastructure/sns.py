"""Amazon SNS topics for async pub/sub notifications.

Used to decouple processing phases (e.g. Textract completion → extraction
queue) and to fan out notifications to multiple subscribers.
"""
from __future__ import annotations

import pulumi
import pulumi_aws as aws


class SnsTopic:
    """An SNS topic with optional SQS subscription.

    Args:
        prefix: Project prefix for naming.
        stack: Stack name (dev/prod).
        name: Logical topic name (e.g. "textract-complete").
    """

    def __init__(self, prefix: str, stack: str, *, name: str):
        topic_name = f"{prefix}-{stack}-{name}"
        self.topic = aws.sns.Topic(
            topic_name,
            name=topic_name,
            tags={"app": prefix, "stack": stack},
        )

    def subscribe_sqs(self, queue_arn: pulumi.Output[str], name_suffix: str):
        """Subscribe an SQS queue to this topic."""
        aws.sns.TopicSubscription(
            f"{self.topic._name}-sub-{name_suffix}",
            topic=self.topic.arn,
            protocol="sqs",
            endpoint=queue_arn,
        )

    @property
    def arn(self) -> pulumi.Output[str]:
        return self.topic.arn
