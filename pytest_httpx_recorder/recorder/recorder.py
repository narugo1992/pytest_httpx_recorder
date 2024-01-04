"""
This module provides a class to record HTTP requests and responses using the `httpx` library.
It allows users to capture and analyze HTTP traffic for testing and debugging purposes.

Classes:
    ResRecorder: Records HTTP requests and responses.

Functions:
    _mocked_handle_request: Mocks the handle_request method of httpx.HTTPTransport.
    _mocked_handle_async_request: Mocks the handle_async_request method of httpx.AsyncHTTPTransport.
"""

import copy
from contextlib import contextmanager, asynccontextmanager
from typing import List, Set

import httpx
from httpx._utils import normalize_header_key
from pytest import MonkeyPatch

from .base import RecordedRequest, RecordedResponse, get_dict_headers

_HEADERS_DEFAULT_BLACKLIST = ['user-agent', 'cookie']
_HEADERS_BLACKLIST_NOTSET = object()

_REAL_HANDLE_REQUEST = httpx.HTTPTransport.handle_request
_REAL_HANDLE_ASYNC_REQUEST = httpx.AsyncHTTPTransport.handle_async_request


class ResRecorder:
    """
    A class to record HTTP requests and responses.

    :param record_request_headers: Flag to determine if request headers should be recorded.
    :type record_request_headers: bool
    :param request_headers_blacklist: List of header keys to exclude from recording.
    :type request_headers_blacklist: List[str]
    :param record_request_content: Flag to determine if request content should be recorded.
    :type record_request_content: bool

    :ivar responses: List of recorded responses.
    :vartype responses: List[RecordedResponse]
    """

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
        """
        Adds a recorded response to the responses list.

        :param request: The HTTP request object.
        :type request: httpx.Request
        :param response: The HTTP response object.
        :type response: httpx.Response
        """
        self.responses.append(RecordedResponse(
            request=RecordedRequest(
                method=request.method,
                url=str(request.url),
                headers=(
                    {
                        key: value for key, value in get_dict_headers(request.headers).items()
                        if normalize_header_key(key, lower=True) not in self.request_headers_blacklist
                    } if self.record_request_headers else {}
                ),
                content=request.content if self.record_request_content else None,
            ),
            status_code=response.status_code,
            http_version=response.http_version,
            headers=get_dict_headers(response.headers),
            content=response.content,
        ))

    def _patch(self):
        """
        Patches the `handle_request` and `handle_async_request` methods of the httpx transport classes.

        :return: MonkeyPatch instance used for patching.
        :rtype: MonkeyPatch
        """
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
            await response.aread()
            self._add_response(request, response)
            return response

        monkeypatch.setattr(
            httpx.AsyncHTTPTransport,
            "handle_async_request",
            _mocked_handle_async_request,
        )

        return monkeypatch

    @contextmanager
    def record(self):
        """
        A context manager for recording synchronous HTTP requests and responses.

        :yields: None
        """
        monkeypatch = self._patch()
        try:
            yield
        finally:
            monkeypatch.undo()

    @asynccontextmanager
    async def async_record(self):
        """
        An async context manager for recording asynchronous HTTP requests and responses.

        :yields: None
        """
        monkeypatch = self._patch()
        try:
            yield
        finally:
            monkeypatch.undo()

    def to_resset(self):
        """
        Converts the recorded responses to a ResSet object.

        :return: ResSet object containing the recorded responses.
        :rtype: ResSet
        """
        from .set import ResSet
        return ResSet(self.responses)
