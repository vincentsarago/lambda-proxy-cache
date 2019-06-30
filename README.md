# lambda-proxy-cache

[![Packaging status](https://badge.fury.io/py/lambda-proxy-cache.svg)](https://badge.fury.io/py/lambda-proxy-cache)
[![CircleCI](https://circleci.com/gh/vincentsarago/lambda-proxy-cache.svg?style=svg)](https://circleci.com/gh/vincentsarago/lambda-proxy-cache)
[![codecov](https://codecov.io/gh/vincentsarago/lambda-proxy-cache/branch/master/graph/badge.svg)](https://codecov.io/gh/vincentsarago/lambda-proxy-cache)

Add a caching layer to [lambda-proxy](https://github.com/vincentsarago/lambda-proxy)

<img width="600" src="https://user-images.githubusercontent.com/10407788/60379162-e50a2880-99fb-11e9-8855-d42ec9b16fbf.png">

## Install

```bash
$ pip install -U pip
$ pip install lambda-proxy-cache
```

Or install from source:

```bash
$ git clone https://github.com/vincentsarago/lambda-proxy-cache.git
$ cd lambda-proxy-cache
$ pip install -U pip
$ pip install -e .
```

# Usage

```python
from lambda_proxy_cache.proxy import API
from lambda_proxy_cache.backends.memcache import MemcachedCache

app = API(name="app", cache_layer=MemcachedCache("MyHostURL"))

@app.route('/user/<name>')
def print_name(name):
    # Do something here
    ...
    return ('OK', 'plain/text', name)

# By adding `no_cache=True` we tell the proxy to not use the cache
@app.route('/user/<name>/id', no_cache=True)
def print_id(name):
    # Do something here
    ...
    return ('OK', 'plain/text', id)
```

# Contribution & Devellopement

Issues and pull requests are more than welcome.

**Dev install & Pull-Request**

```bash
$ git clone https://github.com/vincentsarago/lambda-proxy-cache.git
$ cd lambda-proxy-cache
$ pip install -e .[dev]
```

This repo is set to use pre-commit to run *flake8*, *pydocstring* and *black* ("uncompromising Python code formatter") when committing new code.

```bash
$ pre-commit install
$ git add .
$ git commit -m'my change'
   black.........................Passed
   Flake8........................Passed
   Verifying PEP257 Compliance...Passed
$ git push origin
```
