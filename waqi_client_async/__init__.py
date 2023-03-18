"""An asynchronous client to query data from
the World Air Quality Index project (aqicn.org, waqi.info).
"""

from aiohttp import ClientError, ClientResponse, ClientSession, ClientTimeout
from types import TracebackType
from typing import Any, Optional, Type

import logging

from .exceptions import (
    APIError,
    ConnectionFailed,
    InvalidToken,
    OverQuota,
    TimeoutError.
    UnknownCity,
    UnknownID,
)

LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.waqi.info/"
FEED_URL = BASE_URL + "feed/{}/"
SEARCH_URL = BASE_URL + "search/"
TIMEOUT = 30


def assert_valid(result: dict) -> None:
    if (status := result.get("status")) is not None:
        if status == "ok":
            if (data := result.get("data")) is not None:
                # data = []
                if not data:
                    raise UnknownCity()
                if data.get("msg") == "Unknown ID":
                    raise UnknownID()
                return

            # no data in result:
            raise APIError(result)

        if status == "error":
            if (data := result.get("data")) is not None:
                if data == "Invalid key":
                    raise InvalidToken()
                if data == "Over quota":
                    raise OverQuota()
                # unknown data for status = error
                raise APIError(data)

        # unknown status in result
        raise APIError(status)

    # no status in result, look for specific feed-search error
    elif "Invalid key" in result["rxs"]["obs"][0]["msg"]:
        raise InvalidToken()


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

    async def get(self, path: str, **kwargs: Any) -> dict:
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
            raise ConnectionFailed("Connection to API failed")
        except asyncio.TimeoutError as err:
            raise TimeoutError("Connection to API timed out")

        LOGGER.debug("JSON Data: %s", result)
        assert_valid(result)
        return result["data"]

    async def feed(self, station: str) -> dict:
        """Get the latest information of the given station."""
        return await self.get(FEED_URL.format(station))

    async def search(self, keyword: str) -> dict:
        """Search for stations by name."""
        return await self.get(SEARCH_URL, keyword=keyword)
