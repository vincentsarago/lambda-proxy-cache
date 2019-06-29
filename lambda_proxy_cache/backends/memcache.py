"""Lambda-proxy.cache memcache layer."""

from typing import Dict

import bmemcached

from lambda_proxy.cache.base import LambdaProxyCacheBase


class MemcachedCache(LambdaProxyCacheBase):
    """Memcached Cache."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 11211,
        time: int = 432000,
        **kwargs: Dict,
    ):
        """
        Memcached-backed object.

        Parameters
        ----------
        host: string, redis host
        port: integer
        kwargs: passed directly to bmemcached.Client connection

        """
        # memcache
        self.memcache = bmemcached.Client((f"{host}:{port}",), **kwargs)
        self.timeout = time

    def set(self, key: str, value) -> bool:
        """Set item in Memcached database."""
        return self.memcache.set(key, value, time=self.timeout)

    def get(self, key: str):
        """Get item in Memcached database."""
        return self.memcache.get(key)
