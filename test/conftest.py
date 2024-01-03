import httpx
import pytest
from hbutils.string import plural_word


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False


real_handle_request = httpx.HTTPTransport.handle_request
real_handle_async_request = httpx.AsyncHTTPTransport.handle_async_request


@pytest.fixture
def no_reqs(monkeypatch):
    count = 0

    def mocked_handle_request(
            transport: httpx.HTTPTransport, request: httpx.Request
    ) -> httpx.Response:
        resp = real_handle_request(transport, request)
        nonlocal count
        count += 1
        return resp

    monkeypatch.setattr(
        httpx.HTTPTransport,
        "handle_request",
        mocked_handle_request,
    )

    # Mock asynchronous requests

    async def mocked_handle_async_request(
            transport: httpx.AsyncHTTPTransport, request: httpx.Request
    ) -> httpx.Response:
        resp = await real_handle_async_request(transport, request)
        nonlocal count
        count += 1
        return resp

    monkeypatch.setattr(
        httpx.AsyncHTTPTransport,
        "handle_async_request",
        mocked_handle_async_request,
    )

    try:
        yield
    finally:
        assert count == 0, f'No requests allowed, but {plural_word(count, "request")} detected.'
