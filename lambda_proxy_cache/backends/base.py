"""Lambda-proxy.cache abc class."""

import abc


class LambdaProxyCacheBase(abc.ABC):
    """Abstract base class for lambda proxy cache objects."""

    @abc.abstractmethod
    def set(self, key: str, value) -> bool:
        """
        Set item in db.

        Parameters
        ----------
        key: string
        value:

        Returns
        -------
        bool

        """

    @abc.abstractmethod
    def get(self, key: str):
        """
        Get item in db.

        Parameters
        ----------
        key: string

        Returns
        -------

        """
