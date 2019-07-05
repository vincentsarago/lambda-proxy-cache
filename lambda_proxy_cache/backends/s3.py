"""Lambda-proxy.cache s3 layer."""

from typing import Dict

import json
from boto3.session import Session as boto3_session

from lambda_proxy_cache.backends.base import LambdaProxyCacheBase


class S3Cache(LambdaProxyCacheBase):
    """
    AWS S3 Cache handler.

    - Object expiration is handled by Bucket rules
    https://aws.amazon.com/fr/blogs/aws/amazon-s3-object-expiration/

    """

    def __init__(self, bucket, prefix: str = "", **kwargs: Dict):
        """
        S3-backed cache.

        Parameters
        ----------
        bucket: string, AWS S3 bucket
        kwargs: passed directly to boto3.session.Session connection

        """
        session = boto3_session(**kwargs)
        self.client = session.client("s3")
        self.bucket = bucket
        self.prefix = prefix

    def set(self, key: str, value) -> bool:
        """Set item in AWS S3."""
        key = f"{self.prefix}/{key}" if self.prefix else key
        try:
            return self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(value, default=str).encode(),
            )
        except Exception:
            return False

    def get(self, key: str):
        """Get item in AWS S3."""
        key = f"{self.prefix}/{key}" if self.prefix else key
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response["Body"].read().decode())
        except Exception:
            return None
