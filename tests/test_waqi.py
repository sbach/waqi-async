import pytest


def test_import() -> None:
    """Ensure the Python module can be imported."""
    import waqi_client_async  # noqa: F401

    assert "Success."


@pytest.mark.asyncio
async def test_invalid_feed_query() -> None:
    """Ensure an API call to get a station feed fails if none is provided."""
    import waqi_client_async

    client = waqi_client_async.WAQIClient("")
    with pytest.raises(waqi_client_async.APIError):
        await client.feed("")


@pytest.mark.asyncio
async def test_invalid_token() -> None:
    """Ensure an API call with an invalid token fails."""
    import waqi_client_async

    client = waqi_client_async.WAQIClient("invalid_token")
    with pytest.raises(waqi_client_async.InvalidToken):
        await client.feed("beijing")
