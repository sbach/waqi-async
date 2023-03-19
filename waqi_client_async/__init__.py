"""An asynchronous client to query data from
the World Air Quality Index project (aqicn.org, waqi.info).
"""
import asyncio
import logging

from types import TracebackType
from typing import Any, Optional, Type
from aiohttp import ClientError, ClientResponse, ClientSession, ClientTimeout

from .const import BASE_URL, FEED_URL, SEARCH_URL, TIMEOUT
from .helper import assert_valid
from .exceptions import ConnectionFailed, WaqiTimeoutError

LOGGER = logging.getLogger(__name__)


class WAQIClient:
    """World Air Quality Index API Client."""

    def __init__(self, token: str, session: Optional[ClientSession] = None) -> None:
        timeout = ClientTimeout(total=TIMEOUT)
        self._params = {"token": token}

        if session:
            self._session = session
        else:
            self._session = ClientSession(timeout=timeout, raise_for_status=True)

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the client's session."""
        await self._session.close()

    async def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """Call the WAQI API and return the resulting data (and potiential errors)."""
        resp: ClientResponse

        try:
            async with self._session.get(
                path, params=dict(self._params, **kwargs), timeout=TIMEOUT
            ) as resp:
                result = await resp.json()
                if not isinstance(result, dict):
                    raise TypeError("JSON response was decoded to an unsupported type")
        except ClientError as err:
            raise ConnectionFailed("Connection to API failed") from err
        except asyncio.TimeoutError as err:
            raise WaqiTimeoutError("Connection to API timed out") from err

        LOGGER.debug("JSON Data: %s", result)
        assert_valid(result)
        return result["data"]

    async def feed(self, station_id: str) -> dict[str, Any]:
        """Get the latest information of the given station."""
        return await self.get(FEED_URL.format(station_id))

    async def search(self, keyword: str) -> dict[str, Any]:
        """Search for stations by name."""
        return await self.get(SEARCH_URL, keyword=keyword)
