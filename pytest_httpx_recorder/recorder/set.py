"""
This module provides the ResSet class for managing sets of recorded HTTP responses,
along with functionality to save and load these sets from the filesystem.

Classes:
    ResSet: Manages a set of RecordedResponse objects.

Functions:
    _fake_get_content_decoder: Overrides the default content decoder in httpx.Response.
"""

import os.path
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List

import httpx
import yaml
from hbutils.encoding import base64_encode, base64_decode
from httpx._decoders import IdentityDecoder
from pytest import MonkeyPatch
from pytest_httpx import HTTPXMock

from .base import RecordedResponse, RecordedRequest

_REAL_GET_CONTENT_DECODER = httpx.Response._get_content_decoder


def _fake_get_content_decoder(self):
    """
    A fake content decoder that overrides the default method in httpx.Response.

    :return: An IdentityDecoder instance.
    :rtype: IdentityDecoder
    """
    _ = self
    return IdentityDecoder()


@dataclass(repr=True, eq=True)
class ResSet:
    """
    A data class for managing a set of RecordedResponse objects.

    :param responses: A list of RecordedResponse objects.
    :type responses: List[RecordedResponse]
    """

    responses: List[RecordedResponse]

    def add_to_mock(self, mock: HTTPXMock):
        """
        Adds all recorded responses in this set to an HTTPXMock object.

        :param mock: The mock to add responses to.
        :type mock: HTTPXMock
        """
        for response in self.responses:
            response.add_to_mock(mock)

    @contextmanager
    def mock_context(self, mock: HTTPXMock):
        """
        A context manager to set up a mock HTTP environment using the recorded responses.

        :param mock: The mock to use in the context.
        :type mock: HTTPXMock

        :yields: The configured HTTPXMock object.
        """
        monkeypatch = MonkeyPatch()
        try:
            monkeypatch.setattr(
                httpx.Response,
                '_get_content_decoder',
                _fake_get_content_decoder,
            )
            self.add_to_mock(mock)

            yield mock

        finally:
            monkeypatch.undo()

    def save(self, index_dir: str):
        """
        Saves the recorded responses to the filesystem.

        :param index_dir: Directory where responses will be saved.
        :type index_dir: str
        """
        index_file = os.path.join(index_dir, 'index.yaml')
        os.makedirs(index_dir, exist_ok=True)

        records = []
        for response in self.responses:
            resp_uuid = str(uuid.uuid4())
            resp_content_file = f'resp_{resp_uuid}.bin'
            with open(os.path.join(index_dir, resp_content_file), 'wb') as f:
                f.write(response.content)

            records.append({
                'request': {
                    'method': response.request.method,
                    'url': response.request.url,
                    'headers': response.request.headers,
                    'content': base64_encode(response.request.content)
                    if response.request.content is not None else None,
                },
                'response': {
                    'status_code': response.status_code,
                    'http_version': response.http_version,
                    'headers': response.headers,
                    'content_file': resp_content_file,
                }
            })

        with open(index_file, 'w') as f:
            yaml.dump({'responses': records}, f)

    @classmethod
    def load(cls, index_dir: str, ignore_request_headers: bool = False,
             ignore_request_body: bool = False) -> 'ResSet':
        """
        Loads a set of recorded responses from the filesystem.

        :param index_dir: Directory where responses are stored.
        :type index_dir: str
        :param ignore_request_headers: Flag to ignore request headers while loading.
        :type ignore_request_headers: bool
        :param ignore_request_body: Flag to ignore request body while loading.
        :type ignore_request_body: bool

        :return: An instance of ResSet loaded with the recorded responses.
        :rtype: ResSet
        """
        index_file = os.path.join(index_dir, 'index.yaml')
        with open(index_file, 'r') as f:
            raw_data = yaml.safe_load(f)

        responses = []
        for item in raw_data['responses']:
            request_data = item['request']
            request = RecordedRequest(
                method=request_data['method'],
                url=request_data['url'],
                headers=request_data['headers'] if not ignore_request_headers else {},
                content=(base64_decode(request_data['content'])
                         if not ignore_request_body and request_data['content'] is not None else None),
            )

            response_data = item['response']
            with open(os.path.join(index_dir, response_data['content_file']), 'rb') as f:
                content = f.read()
            response = RecordedResponse(
                request=request,
                status_code=response_data['status_code'],
                http_version=response_data['http_version'],
                headers=response_data['headers'],
                content=content,
            )
            responses.append(response)

        return ResSet(responses)
