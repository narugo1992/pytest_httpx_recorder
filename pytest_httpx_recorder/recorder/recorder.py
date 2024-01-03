import copy
from contextlib import contextmanager
from typing import List, Set

import httpx
from httpx._utils import normalize_header_key
from pytest import MonkeyPatch

from .base import RecordedRequest, RecordedResponse

_HEADERS_DEFAULT_BLACKLIST = [
    'user-agent',
    'cookie',
]
_HEADERS_BLACKLIST_NOTSET = object()

_REAL_HANDLE_REQUEST = httpx.HTTPTransport.handle_request
_REAL_HANDLE_ASYNC_REQUEST = httpx.AsyncHTTPTransport.handle_async_request


class ResRecorder:
    def __init__(self, record_request_headers: bool = True,
                 request_headers_blacklist: List[str] = _HEADERS_BLACKLIST_NOTSET,
                 record_request_content: bool = True):
        self.record_request_headers = record_request_headers
        if request_headers_blacklist is _HEADERS_BLACKLIST_NOTSET:
            self.request_headers_blacklist = copy.deepcopy(_HEADERS_DEFAULT_BLACKLIST)
        else:
            self.request_headers_blacklist = request_headers_blacklist
        self.request_headers_blacklist: Set[str] = {
            normalize_header_key(key, lower=True) for key in self.request_headers_blacklist
        }
        self.record_request_content = record_request_content

        self.responses: List[RecordedResponse] = []

    def _add_response(self, request: httpx.Request, response: httpx.Response):
        self.responses.append(RecordedResponse(
            request=RecordedRequest(
                method=request.method,
                url=str(request.url),
                headers=dict(httpx.Headers(
                    {
                        key: value for key, value in request.headers.items()
                        if normalize_header_key(key, lower=True) not in self.request_headers_blacklist
                    } if self.record_request_headers else {}
                )),
                content=request.content if self.record_request_content else None,
            ),
            status_code=response.status_code,
            http_version=response.http_version,
            headers=dict(response.headers),
            content=response.content,
        ))

    @contextmanager
    def record(self):
        monkeypatch = MonkeyPatch()

        def _mocked_handle_request(
                transport: httpx.HTTPTransport, request: httpx.Request
        ) -> httpx.Response:
            response = _REAL_HANDLE_REQUEST(transport, request)
            response.read()
            self._add_response(request, response)
            return response

        monkeypatch.setattr(
            httpx.HTTPTransport,
            "handle_request",
            _mocked_handle_request,
        )

        async def _mocked_handle_async_request(
                transport: httpx.AsyncHTTPTransport, request: httpx.Request
        ) -> httpx.Response:
            response = await _REAL_HANDLE_ASYNC_REQUEST(transport, request)
            response.read()
            self._add_response(request, response)
            return response

        monkeypatch.setattr(
            httpx.AsyncHTTPTransport,
            "handle_async_request",
            _mocked_handle_async_request,
        )

        try:
            yield
        finally:
            monkeypatch.undo()

    def to_resset(self):
        from .set import ResSet
        return ResSet(self.responses)
