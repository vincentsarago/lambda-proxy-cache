"""Lambda-proxy-cache dynamodb layer."""

from typing import Dict

import json
import time

from boto3.session import Session as boto3_session

from lambda_proxy_cache.backends.base import LambdaProxyCacheBase


class DynamoDBCache(LambdaProxyCacheBase):
    """
    DynamoDB Cache handler.

    - Table primary key has to be named `key`
    - ttl has to be enable and attribute set to ttl

    """

    def __init__(self, table_name: str, time: int = 432000, **kwargs: Dict):
        """
        dynamodb backed cache.

        Parameters
        ----------
        table_name: string, DynamoDB Table
        kwargs: passed directly to boto3.resource('dynamodb')

        """
        session = boto3_session(**kwargs)
        self.dynamodb = session.client("dynamodb")
        self.table_name = table_name
        self.timeout = time

    def set(self, key: str, value) -> bool:
        """Set item in DynamoDB database."""
        ttl = int(time.time() + self.timeout)
        try:
            self.dynamodb.put_item(
                TableName=self.table_name,
                Item={
                    "key": {"S": key},
                    "content": {"S": json.dumps(value, default=str)},
                    "ttl": {"N": str(ttl)},
                },
            )
        except Exception:
            return None

    def get(self, key: str):
        """Get item in DynamoDB database."""
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name, Key={"key": {"S": key}}
            )
            return json.loads(response["Item"]["content"]["S"])
        except Exception:
            return False
