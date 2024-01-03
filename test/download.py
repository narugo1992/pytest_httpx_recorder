import os

import httpx
from tqdm.auto import tqdm


class DownloadError(Exception):
    pass


def download_file(url, filename, expected_size: int = None, desc=None, session=None, silent: bool = False, **kwargs):
    session = session or httpx.Client(follow_redirects=True)
    with session.stream('GET', url, follow_redirects=True, **kwargs) as response:
        response: httpx.Response
        expected_size = expected_size or response.headers.get('Content-Length', None)
        expected_size = int(expected_size) if expected_size is not None else expected_size

        desc = desc or os.path.basename(filename)
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(filename, 'wb') as f:
            with tqdm(total=expected_size, unit='B', unit_scale=True, unit_divisor=1024, desc=desc) as pbar:
                for chunk in response.iter_bytes(chunk_size=1024):
                    f.write(chunk)
                    pbar.update(len(chunk))

        actual_size = os.path.getsize(filename)
        if expected_size is not None and actual_size != expected_size:
            os.remove(filename)
            raise DownloadError(f"Downloaded file is not of expected size, "
                                f"{expected_size} expected but {actual_size} found.")

        return filename
