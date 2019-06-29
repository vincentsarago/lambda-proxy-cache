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
$ cd lambda-proxy
$ pip install -U pip
$ pip install -e .
```

# Usage

```python
from lambda_proxy_cache.proxy import API
from lambda_proxy_cache.backends.memcache import MemcachedCache

cache = MemcachedCache()
APP = API(name="app", cache_layer=cache)

@APP.route('/test/tests/<id>', methods=['GET'], cors=True)
def print_id(id):
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
