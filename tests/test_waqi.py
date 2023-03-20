import importlib

import pytest

waqi = importlib.import_module("waqi_client_async")
waqi_exceptions = importlib.import_module("waqi_client_async.exceptions")


@pytest.mark.asyncio
async def test_invalid_feed_query() -> None:
    """Ensure an API call to get a station feed fails if none is provided."""
    client = waqi.WAQIClient("")
    with pytest.raises(waqi_exceptions.APIError):
        await client.feed("")


@pytest.mark.asyncio
async def test_invalid_token() -> None:
    """Ensure an API call with an invalid token fails."""
    client = waqi.WAQIClient("invalid_token")
    with pytest.raises(waqi_exceptions.InvalidToken):
        await client.feed("beijing")
