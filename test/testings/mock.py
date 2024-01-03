from contextlib import contextmanager
from typing import Optional, List

import httpx
from hbutils.testing import vpip
from pytest import MonkeyPatch
from pytest_httpx import HTTPXMock

_contain_extra_args = vpip('pytest_httpx') >= '0.26'


@contextmanager
def custom_httpx_mock(
        assert_all_responses_were_requested: bool = False,
        non_mocked_hosts: Optional[List[str]] = None,
):
    monkeypatch = MonkeyPatch()

    # Ensure redirections to www hosts are handled transparently.
    non_mocked_hosts = list(non_mocked_hosts or [])
    missing_www = [
        f"www.{host}" for host in non_mocked_hosts if not host.startswith("www.")
    ]
    non_mocked_hosts += missing_www

    mock = HTTPXMock()

    # Mock synchronous requests
    real_handle_request = httpx.HTTPTransport.handle_request

    def mocked_handle_request(
            transport: httpx.HTTPTransport, request: httpx.Request
    ) -> httpx.Response:
        if request.url.host in non_mocked_hosts:
            return real_handle_request(transport, request)
        if _contain_extra_args:
            return mock._handle_request(transport, request)
        else:
            return mock._handle_request(request)

    monkeypatch.setattr(
        httpx.HTTPTransport,
        "handle_request",
        mocked_handle_request,
    )

    # Mock asynchronous requests
    real_handle_async_request = httpx.AsyncHTTPTransport.handle_async_request

    async def mocked_handle_async_request(
            transport: httpx.AsyncHTTPTransport, request: httpx.Request
    ) -> httpx.Response:
        if request.url.host in non_mocked_hosts:
            return await real_handle_async_request(transport, request)
        if _contain_extra_args:
            return await mock._handle_async_request(transport, request)
        else:
            return await mock._handle_async_request(request)

    monkeypatch.setattr(
        httpx.AsyncHTTPTransport,
        "handle_async_request",
        mocked_handle_async_request,
    )

    try:
        yield mock
    finally:
        mock.reset(assert_all_responses_were_requested)
