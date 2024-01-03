from dataclasses import dataclass, field
from typing import Mapping

import httpx
from pytest_httpx import HTTPXMock


@dataclass(eq=True, repr=True)
class RecordedRequest:
    method: str
    url: str
    headers: Mapping[str, str]
    content: bytes


@dataclass(eq=True)
class RecordedResponse:
    request: RecordedRequest
    status_code: int
    http_version: str
    headers: Mapping[str, str]
    content: bytes = field(repr=False)

    def add_to_mock(self, mock: HTTPXMock):
        mock.add_response(
            status_code=self.status_code,
            http_version=self.http_version,
            headers=httpx.Headers(self.headers),
            content=self.content,
            url=self.request.url,
            method=self.request.method,
            match_headers=self.request.headers,
            match_content=self.request.content,
        )
