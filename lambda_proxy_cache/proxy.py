"""Translate request from AWS api-gateway."""

from typing import Any, Callable, Dict, List, Tuple

import json
import logging
import hashlib

from lambda_proxy import proxy
from lambda_proxy_cache.backends.base import LambdaProxyCacheBase


def get_hash(**kwargs: Any) -> str:
    """Create hash from dict."""
    return hashlib.sha224(
        json.dumps(kwargs, sort_keys=True, default=str).encode()
    ).hexdigest()


class RouteEntry(proxy.RouteEntry):
    """API Route."""

    def __init__(
        self,
        endpoint: Callable,
        path: str,
        methods: List = ["GET"],
        cors: bool = False,
        token: bool = False,
        payload_compression_method: str = "",
        binary_b64encode: bool = False,
        ttl=None,
        description: str = None,
        tag: Tuple = None,
        no_cache: bool = False,
    ) -> None:
        """Initialize route object."""
        self.endpoint = endpoint
        self.path = path
        self.route_regex = proxy._path_to_regex(path)
        self.openapi_path = proxy._path_to_openapi(self.path)
        self.methods = methods
        self.cors = cors
        self.token = token
        self.compression = payload_compression_method
        self.b64encode = binary_b64encode
        self.ttl = ttl
        self.description = description or self.endpoint.__doc__
        self.tag = tag
        self.no_cache = no_cache
        if self.compression and self.compression not in ["gzip", "zlib", "deflate"]:
            raise ValueError(
                f"'{payload_compression_method}' is not a supported compression"
            )


class API(proxy.API):
    """API."""

    def __init__(
        self,
        name: str,
        version: str = "0.0.1",
        description: str = None,
        add_docs: bool = True,
        configure_logs: bool = True,
        debug: bool = False,
        cache_layer: LambdaProxyCacheBase = None,
    ) -> None:
        """Initialize API object."""
        self.name: str = name
        self.description: str = description
        self.version: str = version
        self.routes: Dict = {}
        self.context: Dict = {}
        self.event: Dict = {}
        self.debug: bool = debug
        self.log = logging.getLogger(self.name)
        if configure_logs:
            self._configure_logging()
        if add_docs:
            self.setup_docs()

        if cache_layer and not isinstance(cache_layer, LambdaProxyCacheBase):
            raise TypeError("cache_layer must be an instance of LambdaProxyCacheBase")
        self.cache_layer = cache_layer

    def _add_route(self, path: str, endpoint: callable, **kwargs) -> None:
        methods = kwargs.pop("methods", ["GET"])
        cors = kwargs.pop("cors", False)
        token = kwargs.pop("token", "")
        payload_compression = kwargs.pop("payload_compression_method", "")
        binary_encode = kwargs.pop("binary_b64encode", False)
        ttl = kwargs.pop("ttl", None)
        description = kwargs.pop("description", None)
        tag = kwargs.pop("tag", None)
        no_cache = kwargs.pop("no_cache", None)

        if kwargs:
            raise TypeError(
                "TypeError: route() got unexpected keyword "
                "arguments: %s" % ", ".join(list(kwargs))
            )

        if path in self.routes:
            raise ValueError(
                'Duplicate route detected: "{}"\n'
                "URL paths must be unique.".format(path)
            )

        self.routes[path] = RouteEntry(
            endpoint,
            path,
            methods,
            cors,
            token,
            payload_compression,
            binary_encode,
            ttl,
            description,
            tag,
            no_cache,
        )

    def __call__(self, event: Dict, context: Dict):
        """Initialize route and handlers."""
        self.log.debug(json.dumps(event.get("headers", {})))
        self.log.debug(json.dumps(event.get("queryStringParameters", {})))
        self.log.debug(json.dumps(event.get("pathParameters", {})))

        self.event = event
        self.context = context

        headers = event.get("headers", {}) or {}
        headers = dict((key.lower(), value) for key, value in headers.items())

        resource_path = event.get("path", None)
        if resource_path is None:
            return self.response(
                "NOK",
                "application/json",
                json.dumps({"errorMessage": "Missing route parameter"}),
            )

        if not self._url_matching(resource_path):
            return self.response(
                "NOK",
                "application/json",
                json.dumps(
                    {"errorMessage": "No view function for: {}".format(resource_path)}
                ),
            )

        route_entry = self.routes[self._url_matching(resource_path)]

        request_params = event.get("queryStringParameters", {}) or {}
        if route_entry.token:
            if not self._validate_token(request_params.get("access_token")):
                return self.response(
                    "ERROR",
                    "application/json",
                    json.dumps({"message": "Invalid access token"}),
                )

        http_method = event["httpMethod"]
        if http_method not in route_entry.methods:
            return self.response(
                "NOK",
                "application/json",
                json.dumps(
                    {"errorMessage": "Unsupported method: {}".format(http_method)}
                ),
            )

        request_params.pop("access_token", False)

        function_kwargs = self._get_matching_args(route_entry, resource_path)
        function_kwargs.update(request_params.copy())
        if http_method == "POST":
            function_kwargs.update(dict(body=event.get("body")))

        req = function_kwargs.copy()
        req.update(dict(app_route_id=f"{resource_path}-{self.name}-{self.version}"))
        request_hash = get_hash(**req)

        response = (
            self.cache_layer.get(request_hash)
            if self.cache_layer and not route_entry.no_cache
            else None
        )
        if not response:
            try:
                response = route_entry.endpoint(**function_kwargs)
                if (
                    self.cache_layer
                    and response[0] == "OK"
                    and not route_entry.no_cache
                ):
                    self.cache_layer.set(request_hash, response)

            except Exception as err:
                self.log.error(str(err))
                response = (
                    "ERROR",
                    "application/json",
                    json.dumps({"errorMessage": str(err)}),
                )

        return self.response(
            response[0],
            response[1],
            response[2],
            cors=route_entry.cors,
            accepted_methods=route_entry.methods,
            accepted_compression=headers.get("accept-encoding", ""),
            compression=route_entry.compression,
            b64encode=route_entry.b64encode,
            ttl=route_entry.ttl,
        )
