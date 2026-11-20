"""S3 bucket + CloudFront distribution for a React bundle.

Used twice from `__main__.py` — once for the user app, once for the admin
app. Each call produces an isolated bucket + distribution.
"""
from __future__ import annotations

import json
import pulumi
import pulumi_aws as aws


class FrontendHosting:
    def __init__(self, prefix: str, stack: str, *, app_name: str):
        """`app_name` is something like 'user' or 'admin'."""
        rid = f"{prefix}-{stack}-{app_name}"

        self.bucket = aws.s3.Bucket(
            f"{rid}-fe",
            bucket=f"{rid}-fe",
            tags={"app": prefix, "stack": stack, "frontend": app_name},
        )
        aws.s3.BucketPublicAccessBlock(
            f"{rid}-fe-block",
            bucket=self.bucket.id,
            block_public_acls=True,
            block_public_policy=True,
            ignore_public_acls=True,
            restrict_public_buckets=True,
        )

        oac = aws.cloudfront.OriginAccessControl(
            f"{rid}-fe-oac",
            name=f"{rid}-fe-oac",
            origin_access_control_origin_type="s3",
            signing_behavior="always",
            signing_protocol="sigv4",
        )

        self.cdn = aws.cloudfront.Distribution(
            f"{rid}-fe-cdn",
            enabled=True,
            default_root_object="index.html",
            origins=[aws.cloudfront.DistributionOriginArgs(
                domain_name=self.bucket.bucket_regional_domain_name,
                origin_id="s3",
                origin_access_control_id=oac.id,
            )],
            default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
                target_origin_id="s3",
                viewer_protocol_policy="redirect-to-https",
                allowed_methods=["GET", "HEAD", "OPTIONS"],
                cached_methods=["GET", "HEAD"],
                forwarded_values=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
                    query_string=False,
                    cookies=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(forward="none"),
                ),
            ),
            price_class="PriceClass_100",
            restrictions=aws.cloudfront.DistributionRestrictionsArgs(
                geo_restriction=aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
                    restriction_type="none",
                ),
            ),
            viewer_certificate=aws.cloudfront.DistributionViewerCertificateArgs(
                cloudfront_default_certificate=True,
            ),
            custom_error_responses=[
                aws.cloudfront.DistributionCustomErrorResponseArgs(
                    error_code=403, response_code=200, response_page_path="/index.html",
                ),
                aws.cloudfront.DistributionCustomErrorResponseArgs(
                    error_code=404, response_code=200, response_page_path="/index.html",
                ),
            ],
            tags={"app": prefix, "stack": stack, "frontend": app_name},
        )

        aws.s3.BucketPolicy(
            f"{rid}-fe-policy",
            bucket=self.bucket.id,
            policy=pulumi.Output.all(self.bucket.arn, self.cdn.arn).apply(
                lambda args: json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": {"Service": "cloudfront.amazonaws.com"},
                        "Action": "s3:GetObject",
                        "Resource": f"{args[0]}/*",
                        "Condition": {"StringEquals": {"AWS:SourceArn": args[1]}},
                    }],
                })
            ),
        )
