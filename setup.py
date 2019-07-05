"""Setup lambda-proxy-cache."""

from setuptools import setup, find_packages

with open("README.md") as f:
    readme = f.read()

inst_reqs = ["lambda-proxy~=4.1"]

extra_reqs = {
    "aws": ["boto3"],
    "memcache": ["python-binary-memcached"],
    "test": ["pytest", "pytest-cov", "mock"],
    "dev": ["pytest", "pytest-cov", "mock", "pre-commit"],
}

setup(
    name="lambda-proxy-cache",
    version="0.0.1dev4",
    description=u"Add cache to lambda-proxy",
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires=">=3",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="AWS-Lambda API-Gateway Request Proxy cache",
    author=u"Vincent Sarago",
    author_email="vincent.sarago@gmail.com",
    url="https://github.com/vincentsarago/lambda-proxy-cache",
    license="BSD-3",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
