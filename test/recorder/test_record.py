from unittest import skipUnless

import httpx
import pytest
from hbutils.testing import vpython, OS

from pytest_httpx_recorder.recorder import ResRecorder


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return True


@pytest.mark.unittest
class TestRecorderRecord:
    def test_record_sync_simple(self):
        recorder = ResRecorder()
        with recorder.record():
            client = httpx.Client(follow_redirects=True)
            resp = client.get('https://danbooru.donmai.us/artists/167715.json')
            resp.raise_for_status()
            assert resp.json() == {
                "id": 167715,
                "created_at": "2018-04-28T20:38:35.401-04:00",
                "name": "kamizaki_hibana",
                "updated_at": "2022-03-17T02:42:11.764-04:00",
                "is_deleted": False,
                "group_name": "",
                "is_banned": False,
                "other_names": ["紙坂ひばな", "187kami", "eco_co3", "binetsu", "微熱", "かなりのびねつ", "36度5分",
                                "36_5_binetsu", "kyohorabetai", "びねつ", "takoyakibinetsu", "kanari_no_binetsu"]
            }

        assert len(recorder.responses) == 1
        resp = recorder.responses[0]
        req = resp.request
        assert req.method == 'GET'
        assert req.url == 'https://danbooru.donmai.us/artists/167715.json'
        assert req.headers.get('Host') == 'danbooru.donmai.us'
        assert req.headers.get('Accept-Encoding') == 'gzip, deflate'
        assert req.content == b''

        assert resp.status_code == 200
        assert len(resp.content) >= 300
        assert resp.headers['Content-Encoding'] == 'gzip'

    @skipUnless(vpython < '3.11' or not OS.windows, 'Do not run on windows python3.11')
    async def test_record_async_simple(self):
        recorder = ResRecorder()
        async with recorder.async_record():
            client = httpx.AsyncClient(follow_redirects=True)
            resp = await client.get('https://danbooru.donmai.us/artists/167715.json')
            resp.raise_for_status()
            assert resp.json() == {
                "id": 167715,
                "created_at": "2018-04-28T20:38:35.401-04:00",
                "name": "kamizaki_hibana",
                "updated_at": "2022-03-17T02:42:11.764-04:00",
                "is_deleted": False,
                "group_name": "",
                "is_banned": False,
                "other_names": ["紙坂ひばな", "187kami", "eco_co3", "binetsu", "微熱", "かなりのびねつ", "36度5分",
                                "36_5_binetsu", "kyohorabetai", "びねつ", "takoyakibinetsu", "kanari_no_binetsu"]
            }

        assert len(recorder.responses) == 1
        resp = recorder.responses[0]
        req = resp.request
        assert req.method == 'GET'
        assert req.url == 'https://danbooru.donmai.us/artists/167715.json'
        assert req.headers.get('Host') == 'danbooru.donmai.us'
        assert req.headers.get('Accept-Encoding') == 'gzip, deflate'
        assert req.content == b''

        assert resp.status_code == 200
        assert len(resp.content) >= 300
        assert resp.headers['Content-Encoding'] == 'gzip'
