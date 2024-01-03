import glob
import os.path

import httpx
import pytest
from PIL import Image
from hbutils.testing import isolated_directory

from pytest_httpx_recorder.recorder import ResSet, ResRecorder
from ..download import download_file
from ..testings import get_testfile, custom_httpx_mock


@pytest.fixture()
def danbooru_simple_image() -> Image.Image:
    image = Image.open(get_testfile('danbooru_simple_image.jpg'))
    image.load()
    return image


@pytest.fixture()
def resset_replay(httpx_mock):
    resset = ResSet.load(get_testfile('danbooru_simple'))
    with resset.mock_context(httpx_mock):
        yield


def _header_cmp(h1, h2):
    return all(
        value == h2.get(key)
        for key, value in h1.items()
    )


@pytest.mark.unittest
class TestRecorderSet:
    def test_mock(self, image_diff, danbooru_simple_image):
        recorder = ResRecorder()
        with recorder.record():
            client = httpx.Client(follow_redirects=True)
            resp = client.get('https://danbooru.donmai.us/artists/167715.json')
            resp.raise_for_status()
            _std_json = resp.json()
            _std_headers = resp.headers

            download_file(
                url='https://cdn.donmai.us/original/9b/25/__akisato_konoha_uehara_meiko_shimoda_kaori_yamada_touya_rokuta_mamoru_and_4_more_comic_party_and_1_more__9b257058ee0866d554d01e9036ecb3b6.jpg',
                filename='test_image.jpg',
            )

        assert len(recorder.responses) == 2

        with custom_httpx_mock() as mock:
            with recorder.to_resset().mock_context(mock):
                resp = client.get('https://danbooru.donmai.us/artists/167715.json')
                assert resp.json() == _std_json
                assert _header_cmp(_std_headers, resp.headers)
                with isolated_directory():
                    download_file(
                        url='https://cdn.donmai.us/original/9b/25/__akisato_konoha_uehara_meiko_shimoda_kaori_yamada_touya_rokuta_mamoru_and_4_more_comic_party_and_1_more__9b257058ee0866d554d01e9036ecb3b6.jpg',
                        filename='test_image.jpg',
                    )

                    assert image_diff(
                        Image.open('test_image.jpg'),
                        danbooru_simple_image,
                        throw_exception=False
                    ) < 1e-2

    def test_save_to_local(self, image_diff, danbooru_simple_image):
        recorder = ResRecorder()
        with recorder.record():
            client = httpx.Client(follow_redirects=True)
            resp = client.get('https://danbooru.donmai.us/artists/167715.json')
            resp.raise_for_status()
            _std_json = resp.json()
            _std_headers = resp.headers

            download_file(
                url='https://cdn.donmai.us/original/9b/25/__akisato_konoha_uehara_meiko_shimoda_kaori_yamada_touya_rokuta_mamoru_and_4_more_comic_party_and_1_more__9b257058ee0866d554d01e9036ecb3b6.jpg',
                filename='test_image.jpg',
            )

        assert len(recorder.responses) == 2
        with isolated_directory():
            dst_dir = os.path.abspath('ff')
            recorder.to_resset().save('ff')
            assert os.path.exists(os.path.join(dst_dir, 'index.yaml'))
            assert len(glob.glob(os.path.join(dst_dir, '*.bin'))) == 2

            with custom_httpx_mock() as mock:
                resset = ResSet.load('ff')
                with resset.mock_context(mock):
                    resp = client.get('https://danbooru.donmai.us/artists/167715.json')
                    assert resp.json() == _std_json
                    assert _header_cmp(_std_headers, resp.headers)
                    with isolated_directory():
                        download_file(
                            url='https://cdn.donmai.us/original/9b/25/__akisato_konoha_uehara_meiko_shimoda_kaori_yamada_touya_rokuta_mamoru_and_4_more_comic_party_and_1_more__9b257058ee0866d554d01e9036ecb3b6.jpg',
                            filename='test_image.jpg',
                        )

                        assert image_diff(
                            Image.open('test_image.jpg'),
                            danbooru_simple_image,
                            throw_exception=False
                        ) < 1e-2

    def test_mock_sync_danbooru(self, resset_replay, image_diff, danbooru_simple_image):
        client = httpx.Client(follow_redirects=True)

        assert client.get('https://danbooru.donmai.us/artists/167715.json').json() == {
            "id": 167715,
            "created_at": "2018-04-28T20:38:35.401-04:00",
            "name": "kamizaki_hibana",
            "updated_at": "2022-03-17T02:42:11.764-04:00",
            "is_deleted": False,
            "group_name": "",
            "is_banned": False,
            "other_names": ["紙坂ひばな", "187kami", "eco_co3", "binetsu", "微熱", "かなりのびねつ", "36度5分", "36_5_binetsu",
                            "kyohorabetai", "びねつ", "takoyakibinetsu", "kanari_no_binetsu"]
        }
        with isolated_directory():
            download_file(
                url='https://cdn.donmai.us/original/9b/25/__akisato_konoha_uehara_meiko_shimoda_kaori_yamada_touya_rokuta_mamoru_and_4_more_comic_party_and_1_more__9b257058ee0866d554d01e9036ecb3b6.jpg',
                filename='test_image.jpg',
            )

            assert image_diff(
                Image.open('test_image.jpg'),
                danbooru_simple_image,
                throw_exception=False
            ) < 1e-2

    async def test_mock_async_danbooru(self, resset_replay):
        client = httpx.AsyncClient(follow_redirects=True)
        response = await client.get('https://danbooru.donmai.us/artists/167715.json')
        assert response.json() == {
            "id": 167715,
            "created_at": "2018-04-28T20:38:35.401-04:00",
            "name": "kamizaki_hibana",
            "updated_at": "2022-03-17T02:42:11.764-04:00",
            "is_deleted": False,
            "group_name": "",
            "is_banned": False,
            "other_names": ["紙坂ひばな", "187kami", "eco_co3", "binetsu", "微熱", "かなりのびねつ", "36度5分", "36_5_binetsu",
                            "kyohorabetai", "びねつ", "takoyakibinetsu", "kanari_no_binetsu"]
        }
