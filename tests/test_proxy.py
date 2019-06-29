"""Test lambda-proxy-cache."""

from mock import Mock

from lambda_proxy_cache import proxy
from lambda_proxy_cache.backends.base import LambdaProxyCacheBase


def test_proxy_API_nocache():
    """Test proxy without caching."""
    app = proxy.API(name="test")
    funct = Mock(__name__="Mock", return_value=("OK", "text/plain", "heyyyy"))
    app._add_route("/test/<string:user>/<name>", funct, methods=["GET"], cors=True)

    event = {
        "path": "/test/remote/pixel",
        "httpMethod": "GET",
        "headers": {},
        "queryStringParameters": {},
    }
    resp = {
        "body": "heyyyy",
        "headers": {
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "text/plain",
        },
        "statusCode": 200,
    }
    res = app(event, {})
    assert res == resp
    funct.assert_called_with(user="remote", name="pixel")

    for h in app.log.handlers:
        app.log.removeHandler(h)


def test_proxy_API_cache():
    """Test proxy with caching."""
    cache = Mock(LambdaProxyCacheBase)
    cache.get.return_value = ("OK", "text/plain", "heyyyy")

    app = proxy.API(name="test", cache_layer=cache)
    funct = Mock(__name__="Mock", return_value=("OK", "text/plain", "heyyyy"))
    app._add_route("/test/<string:user>/<name>", funct, methods=["GET"], cors=True)

    event = {
        "path": "/test/remote/pixel",
        "httpMethod": "GET",
        "headers": {},
        "queryStringParameters": {},
    }
    resp = {
        "body": "heyyyy",
        "headers": {
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "text/plain",
        },
        "statusCode": 200,
    }
    res = app(event, {})
    assert res == resp
    funct.assert_not_called()
    cache.get.assert_called_once()
    cache.set.assert_not_called()

    for h in app.log.handlers:
        app.log.removeHandler(h)


def test_proxy_API_cacheEmpty():
    """Test proxy with caching."""
    cache = Mock(LambdaProxyCacheBase)
    cache.get.return_value = None
    cache.set.return_value = True

    app = proxy.API(name="test", cache_layer=cache)
    funct = Mock(__name__="Mock", return_value=("OK", "text/plain", "heyyyy"))
    app._add_route("/test/<string:user>/<name>", funct, methods=["GET"], cors=True)

    event = {
        "path": "/test/remote/pixel",
        "httpMethod": "GET",
        "headers": {},
        "queryStringParameters": {},
    }
    resp = {
        "body": "heyyyy",
        "headers": {
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "text/plain",
        },
        "statusCode": 200,
    }
    res = app(event, {})
    assert res == resp
    funct.assert_called_with(user="remote", name="pixel")
    cache.get.assert_called_once()
    cache.set.assert_called_once()

    args = cache.set.call_args
    assert args[0][1] == ("OK", "text/plain", "heyyyy")

    for h in app.log.handlers:
        app.log.removeHandler(h)
