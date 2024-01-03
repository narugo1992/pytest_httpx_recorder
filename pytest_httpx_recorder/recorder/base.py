from dataclasses import dataclass, field
from typing import Dict

import httpx
from pytest_httpx import HTTPXMock


@dataclass(eq=True, repr=True)
class RecordedRequest:
    method: str
    url: str
    headers: Dict[str, str]
    content: bytes


@dataclass(eq=True)
class RecordedResponse:
    request: RecordedRequest
    status_code: int
    http_version: str
    headers: Dict[str, str]
    content: bytes = field(repr=False)

    def add_to_mock(self, mock: HTTPXMock):
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


def get_dict_headers(headers: httpx.Headers):
    encoding = headers.encoding
    request_headers: Dict[bytes, bytes] = {}
    # Can be cleaned based on the outcome of https://github.com/encode/httpx/discussions/2841
    for raw_name, raw_value in headers.raw:
        if raw_name in request_headers:
            request_headers[raw_name] += b", " + raw_value
        else:
            request_headers[raw_name] = raw_value

    return {
        key.decode(encoding): value.decode(encoding)
        for key, value in request_headers.items()
    }
