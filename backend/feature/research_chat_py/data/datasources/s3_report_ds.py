"""S3 datasource for uploading markdown reports and generating presigned URLs."""
from __future__ import annotations

from datetime import datetime, timezone


class S3ReportDataSource:
    def __init__(self, s3_client, bucket_name: str):
        self._s3 = s3_client
        self._bucket = bucket_name

    def upload_report(self, user_id: str, conversation_id: str, content: str) -> str:
        """Upload markdown content to S3 and return a presigned download URL."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        key = f"reports/{user_id}/{conversation_id}/{timestamp}_report.md"

        self._s3.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=content.encode("utf-8"),
            ContentType="text/markdown",
        )

        url = self._s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=3600,
        )
        return url
