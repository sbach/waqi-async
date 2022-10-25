"""An asynchronous client to query data from
the World Air Quality Index project (aqicn.org, waqi.info).
"""

from aiohttp import ClientSession
from types import TracebackType
from typing import Any, Optional, Type

BASE_URL = "https://api.waqi.info/"
FEED_URL = BASE_URL + "feed/{}/"
SEARCH_URL = BASE_URL + "search/"


class APIError(Exception):
    """Base class for exceptions from the WAQI API."""

    pass


class InvalidToken(APIError):
    """Raised when the provided API token is invalid."""

    pass


class OverQuota(APIError):
    """Raised when the API token used reached its quota."""

    pass


class UnknownStation(APIError):
    """Raised when the provided station could not be found."""

    pass


def assert_valid(result: dict) -> None:
    if result.get("status") != "error":
        return

    data = result.get("data")
    if data == "Invalid key":
        raise InvalidToken()
    elif data == "Over quota":
        raise OverQuota()
    elif data == "Unknown station":
        raise UnknownStation()
    elif data:
        raise APIError(data)

    message = result.get("message")
    if message:
        raise APIError(message)


class WAQIClient:
    """World Air Quality Index API Client."""

    def __init__(self, token: str, session: Optional[ClientSession] = None) -> None:
        self._params = {"token": token}
        if session:
            self._session = session
        else:
            self._session = ClientSession(raise_for_status=True)

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
        async with self._session.get(path, params=dict(self._params, **kwargs)) as r:
            result = await r.json()
            if not isinstance(result, dict):
                raise TypeError("JSON response was decoded to an unsupported type")
            assert_valid(result)
            return result["data"]

    async def feed(self, station: str) -> dict:
        """Get the latest information of the given station."""
        return await self.get(FEED_URL.format(station))

    async def search(self, keyword: str) -> dict:
        """Search for stations by name."""
        return await self.get(SEARCH_URL, keyword=keyword)
