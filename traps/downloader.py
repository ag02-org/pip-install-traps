import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Union, List
from xml.etree import ElementTree

import requests
from click import BadParameter

from traps.utils import filename_from_url
from traps.utils import logger

__all__ = ["get"]
API_URL = "https://safebooru.org/index.php"
MAX_OFFSET = 130  # Do not change.


def _fetch_urls(n: int = 1) -> List[str]:
    if n > 5000:
        raise BadParameter("you can't download more than 5000 files at a time")
    if n < 1:
        raise BadParameter("you can't download a negative number of files")

    used_offsets = []
    urls = []

    def fetch(limit):
        offset = random.randint(1, MAX_OFFSET)
        while offset in used_offsets:
            offset = random.randint(1, MAX_OFFSET)
        else:
            used_offsets.append(offset)
        params = {
            "page": "dapi",
            "s": "post",
            "q": "index",
            "limit": 100,
            "pid": offset,
            "tags": "trap"
        }
        resp = requests.get(API_URL, params)
        posts = ElementTree.fromstring(resp.text).iter("post")
        return [
            next(posts).attrib["file_url"]
            for _ in range(limit)
        ]

    logger.info("Fetching urls")
    if n > 100:
        with ThreadPoolExecutor(max_workers=16) as p:
            for i in p.map(lambda _: fetch(100), range(n // 100)):
                urls += i
            n %= 100
    if n < 100:
        urls += fetch(n)
    logger.info("Done")
    return urls


def _download(directory: Path, url: str) -> None:
    logger.debug(f"Downloading {url}")
    resp = requests.get(url, stream=True)
    if not resp.ok:
        logger.warning(f"Couldn't download {url}: HTTP error {resp.status_code}")
        return
    filename = filename_from_url(url)
    with open(directory / filename, "wb") as f:
        for part in resp.iter_content(1024):
            if not part:
                break
            f.write(part)
        else:
            logger.success(f"Downloaded {url}")


def get(directory: Union[str, Path] = "traps", amount: int = 1) -> None:
    if not isinstance(directory, Path):
        directory = Path(directory)
    if not directory.exists():
        logger.debug(f"Creating {directory.name} directory")
        directory.mkdir()
        logger.debug("Done")
    urls = _fetch_urls(amount)
    logger.info("Downloading traps")
    with ThreadPoolExecutor(max_workers=16) as p:
        p.map(lambda url: _download(directory, url), urls)
    logger.success(f"Downloaded {amount} traps")
