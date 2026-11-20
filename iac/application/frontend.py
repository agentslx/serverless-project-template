"""Frontend bundle upload — used twice (user app + admin app)."""
from __future__ import annotations

import os
import mimetypes

import pulumi
import pulumi_aws as aws


class FrontendBundle:
    def __init__(self, prefix: str, stack: str, *, hosting, bundle_dir: str, app_name: str):
        if not bundle_dir or not os.path.isdir(bundle_dir):
            pulumi.log.warn(
                f"Frontend bundle dir '{bundle_dir}' does not exist for app "
                f"'{app_name}'. Run `yarn build` in the corresponding project "
                "before `pulumi up`."
            )
            return

        for root, _, files in os.walk(bundle_dir):
            for file in files:
                full = os.path.join(root, file)
                rel = os.path.relpath(full, bundle_dir).replace(os.sep, "/")
                ctype, _ = mimetypes.guess_type(full)
                aws.s3.BucketObject(
                    f"{prefix}-{stack}-{app_name}-fe-{rel}",
                    bucket=hosting.bucket.id,
                    key=rel,
                    source=pulumi.FileAsset(full),
                    content_type=ctype or "application/octet-stream",
                    cache_control=(
                        "public, max-age=31536000, immutable"
                        if rel.startswith("static/")
                        else "no-cache"
                    ),
                )
