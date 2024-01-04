"""
This module provides classes and functions for recording HTTP requests and responses,
and for converting HTTPX headers to a dictionary format.

Classes:
    RecordedRequest: Data class for storing details of a recorded HTTP request.
    RecordedResponse: Data class for storing details of a recorded HTTP response.

Functions:
    get_dict_headers(headers): Converts httpx.Headers to a standard Python dictionary.
"""

from dataclasses import dataclass, field
from typing import Dict

import httpx
from pytest_httpx import HTTPXMock


@dataclass(eq=True, repr=True)
class RecordedRequest:
    """
    A data class that represents a recorded HTTP request.

    :param method: The HTTP method of the request.
    :type method: str
    :param url: The URL of the request.
    :type url: str
    :param headers: The headers of the request.
    :type headers: Dict[str, str]
    :param content: The content of the request.
    :type content: bytes
    """

    method: str
    url: str
    headers: Dict[str, str]
    content: bytes


@dataclass(eq=True)
class RecordedResponse:
    """
    A data class that represents a recorded HTTP response.

    :param request: The associated `RecordedRequest` object.
    :type request: RecordedRequest
    :param status_code: The HTTP status code of the response.
    :type status_code: int
    :param http_version: The HTTP version used in the response.
    :type http_version: str
    :param headers: The headers of the response.
    :type headers: Dict[str, str]
    :param content: The content of the response.
    :type content: bytes

    :raises TypeError: If an incompatible type is provided for any field.
    """

    request: RecordedRequest
    status_code: int
    http_version: str
    headers: Dict[str, str]
    content: bytes = field(repr=False)

    def add_to_mock(self, mock: HTTPXMock):
        """
        Adds this recorded response to an HTTPXMock instance.

        :param mock: The HTTPXMock instance to add the response to.
        :type mock: HTTPXMock
        """
        mock.add_response(
            status_code=self.status_code,
            http_version=self.http_version,
            headers=self.headers,
            content=self.content,
            url=self.request.url,
            method=self.request.method,
            match_headers=self.request.headers,
            match_content=self.request.content,
        )


def get_dict_headers(headers: httpx.Headers) -> Dict[str, str]:
    """
    Converts httpx.Headers to a standard Python dictionary.

    :param headers: The httpx.Headers object to convert.
    :type headers: httpx.Headers
    :rtype: Dict[str, str]
    :raises ValueError: If there is an issue decoding the headers.
    """
    encoding = headers.encoding
    request_headers: Dict[bytes, bytes] = {}

    for raw_name, raw_value in headers.raw:
        if raw_name in request_headers:
            request_headers[raw_name] += b", " + raw_value
        else:
            request_headers[raw_name] = raw_value

    return {
        key.decode(encoding): value.decode(encoding)
        for key, value in request_headers.items()
    }
