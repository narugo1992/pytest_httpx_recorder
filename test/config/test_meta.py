import pytest

from pytest_httpx_recorder.config.meta import __TITLE__


@pytest.mark.unittest
class TestConfigMeta:
    def test_title(self):
        assert __TITLE__ == 'pytest_httpx_recorder'
