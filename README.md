# pytest_httpx_recorder

[![PyPI](https://img.shields.io/pypi/v/pytest_httpx_recorder)](https://pypi.org/project/pytest_httpx_recorder/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytest_httpx_recorder)
![Loc](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/narugo1992/5a68529500305d20d093e1ae695a9cf1/raw/loc.json)
![Comments](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/narugo1992/5a68529500305d20d093e1ae695a9cf1/raw/comments.json)

[![Code Test](https://github.com/narugo1992/pytest_httpx_recorder/workflows/Code%20Test/badge.svg)](https://github.com/narugo1992/pytest_httpx_recorder/actions?query=workflow%3A%22Code+Test%22)
[![Package Release](https://github.com/narugo1992/pytest_httpx_recorder/workflows/Package%20Release/badge.svg)](https://github.com/narugo1992/pytest_httpx_recorder/actions?query=workflow%3A%22Package+Release%22)
[![codecov](https://codecov.io/gh/narugo1992/pytest_httpx_recorder/branch/main/graph/badge.svg?token=XJVDP4EFAT)](https://codecov.io/gh/narugo1992/pytest_httpx_recorder)

![GitHub Org's stars](https://img.shields.io/github/stars/narugo1992)
[![GitHub stars](https://img.shields.io/github/stars/narugo1992/pytest_httpx_recorder)](https://github.com/narugo1992/pytest_httpx_recorder/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/narugo1992/pytest_httpx_recorder)](https://github.com/narugo1992/pytest_httpx_recorder/network)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/narugo1992/pytest_httpx_recorder)
[![GitHub issues](https://img.shields.io/github/issues/narugo1992/pytest_httpx_recorder)](https://github.com/narugo1992/pytest_httpx_recorder/issues)
[![GitHub pulls](https://img.shields.io/github/issues-pr/narugo1992/pytest_httpx_recorder)](https://github.com/narugo1992/pytest_httpx_recorder/pulls)
[![Contributors](https://img.shields.io/github/contributors/narugo1992/pytest_httpx_recorder)](https://github.com/narugo1992/pytest_httpx_recorder/graphs/contributors)
[![GitHub license](https://img.shields.io/github/license/narugo1992/pytest_httpx_recorder)](https://github.com/narugo1992/pytest_httpx_recorder/blob/master/LICENSE)

Recorder feature based on pytest_httpx, like recorder feature in responses

## Installation

```shell
pip install pytest_httpx_recorder
```

For more information about installation, you can refer
to [Installation](https://narugo1992.github.io/pytest_httpx_recorder/main/tutorials/installation/index.html).

## Record the Requests

```python
import httpx

from pytest_httpx_recorder.recorder import ResRecorder

if __name__ == '__main__':
    recorder = ResRecorder()
    with recorder.record():
        client = httpx.Client(follow_redirects=True)
        client.get('https://danbooru.donmai.us/artists/167715.json')
        client.head(
            'https://cdn.donmai.us/original/9b/25/__akisato_konoha_uehara_meiko_shimoda_kaori_yamada_touya_rokuta_mamoru_and_4_more_comic_party_and_1_more__9b257058ee0866d554d01e9036ecb3b6.jpg')

    # save to directory 'test_danbooru_simple'
    recorder.to_resset().save('test_danbooru_simple')

```

## Replay in Pytest

```python
import httpx
import pytest

from pytest_httpx_recorder.recorder import ResSet


@pytest.fixture
def replay_from_test_danbooru_simple(httpx_mock):
    resset = ResSet.load('test_danbooru_simple')
    with resset.mock_context(httpx_mock):
        yield


def test_replay(replay_from_test_danbooru_simple):
    client = httpx.Client(follow_redirects=True)
    resp = client.get('https://danbooru.donmai.us/artists/167715.json')
    resp.raise_for_status()

    resp = client.head(
        'https://cdn.donmai.us/original/9b/25/__akisato_konoha_uehara_meiko_shimoda_kaori_yamada_touya_rokuta_mamoru_and_4_more_comic_party_and_1_more__9b257058ee0866d554d01e9036ecb3b6.jpg')
    resp.raise_for_status()

```
