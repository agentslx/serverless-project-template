"""Amazon SQS queues with Dead Letter Queues for event-driven decoupling.

Provides ingestion buffering and resilient message delivery with exponential
retry via redrive policies. Each queue gets a paired DLQ automatically.
"""
from __future__ import annotations

import pulumi
import pulumi_aws as aws


class SqsQueue:
    """An SQS queue with an attached Dead Letter Queue (DLQ).

    Args:
        prefix: Project prefix for naming.
        stack: Stack name (dev/prod).
        name: Logical queue name (e.g. "ocr-tasks", "extraction").
        visibility_timeout: Seconds a message stays invisible after receipt.
        max_receive_count: Retries before routing to DLQ.
        message_retention: Seconds to retain messages (default 4 days).
    """

    def __init__(
        self,
        prefix: str,
        stack: str,
        *,
        name: str,
        visibility_timeout: int = 60,
        max_receive_count: int = 3,
        message_retention: int = 345600,
    ):
        dlq_name = f"{prefix}-{stack}-{name}-dlq"
        self.dlq = aws.sqs.Queue(
            dlq_name,
            name=dlq_name,
            message_retention_seconds=1209600,  # 14 days for DLQ
            tags={"app": prefix, "stack": stack, "purpose": "dlq"},
        )

        queue_name = f"{prefix}-{stack}-{name}"
        self.queue = aws.sqs.Queue(
            queue_name,
            name=queue_name,
            visibility_timeout_seconds=visibility_timeout,
            message_retention_seconds=message_retention,
            redrive_policy=self.dlq.arn.apply(
                lambda arn: pulumi.Output.json_dumps({
                    "deadLetterTargetArn": arn,
                    "maxReceiveCount": max_receive_count,
                })
            ),
            tags={"app": prefix, "stack": stack},
        )

    @property
    def arn(self) -> pulumi.Output[str]:
        return self.queue.arn

    @property
    def url(self) -> pulumi.Output[str]:
        return self.queue.url

    @property
    def dlq_arn(self) -> pulumi.Output[str]:
        return self.dlq.arn
