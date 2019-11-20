"""Translate request from AWS api-gateway."""

from typing import Any, Dict

import json
import base64
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

    def __init__(self, *args, **kwargs) -> None:
        """Initialize route object."""
        self.no_cache = kwargs.pop("no_cache", False)
        super(RouteEntry, self).__init__(*args, **kwargs)


class API(proxy.API):
    """API."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize API object."""
        cache_layer: LambdaProxyCacheBase = kwargs.pop("cache_layer", None)
        super(API, self).__init__(*args, **kwargs)
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
            methods=methods,
            cors=cors,
            token=token,
            payload_compression_method=payload_compression,
            binary_b64encode=binary_encode,
            ttl=ttl,
            description=description,
            tag=tag,
            no_cache=no_cache,
        )

    def __call__(self, event: Dict, context: Dict):
        """Initialize route and handlers."""
        self.log.debug(json.dumps(event, default=str))

        self.event = event
        self.context = context

        # HACK: For an unknown reason some keys can have lower or upper case.
        # To make sure the app works well we cast all the keys to lowercase.
        headers = self.event.get("headers", {}) or {}
        self.event["headers"] = dict(
            (key.lower(), value) for key, value in headers.items()
        )

        self.request_path = proxy.ApigwPath(self.event)
        if self.request_path.path is None:
            return self.response(
                "NOK",
                "application/json",
                json.dumps({"errorMessage": "Missing or invalid path"}),
            )

        if not self._url_matching(self.request_path.path):
            return self.response(
                "NOK",
                "application/json",
                json.dumps(
                    {
                        "errorMessage": "No view function for: {}".format(
                            self.request_path.path
                        )
                    }
                ),
            )

        route_entry = self.routes[self._url_matching(self.request_path.path)]

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

        function_kwargs = self._get_matching_args(route_entry, self.request_path.path)
        function_kwargs.update(request_params.copy())
        if http_method == "POST" and event.get("body"):
            body = event["body"]
            if event.get("isBase64Encoded"):
                body = base64.b64decode(body).decode()
            function_kwargs.update(dict(body=body))

        req = function_kwargs.copy()
        req.update(
            dict(app_route_id=f"{self.request_path.path}-{self.name}-{self.version}")
        )
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
            accepted_compression=self.event["headers"].get("accept-encoding", ""),
            compression=route_entry.compression,
            b64encode=route_entry.b64encode,
            ttl=route_entry.ttl,
        )
