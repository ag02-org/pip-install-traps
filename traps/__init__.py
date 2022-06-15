import os
import secrets
import sys
from typing import Union
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Thread

import click
import requests
from loguru import logger

__version__ = "2.0.0"
API_URL = "https://api.waifu.pics/nsfw/trap"

try:
    logger.remove(0)
except ValueError:
    pass


def fetch_url(urls_list: list = None) -> str:
    url = requests.get(API_URL).json()["url"]
    if urls_list is not None:
        urls_list.append(url)
    return url


def get(directory: Union[str, os.PathLike] = "traps", url: str = None,
        create_dir: bool = True):
    if url is None:
        url = fetch_url()
    directory = Path(directory)
    if not directory.exists() and create_dir:
        directory.mkdir()
    filename = urllib.parse.urlparse(url).path
    filename = directory.joinpath(secrets.token_hex(8) + Path(filename).suffix)
    with open(filename, "wb") as f:
        logger.debug(f"downloading {url}")
        response = requests.get(url, stream=True)
        for block in response.iter_content(1024):
            if not block:
                break
            f.write(block)
        else:
            logger.success(f"downloaded {url}")


@click.command(help="how about you pip install some traps")
@click.option(
    "-n",
    "-t",
    "--traps",
    type=click.INT,
    default=10,
    show_default=True,
    help="number of traps to get"
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="verbose output")
@click.argument(
    "directory",
    default="traps",
    type=click.Path(
        dir_okay=True,
        file_okay=False,
        path_type=Path
    )
)
def main(traps: int, directory: Path, verbose: bool):
    if verbose:
        loglevel = "DEBUG"
    else:
        loglevel = "INFO"
    logger.add(
        sys.stderr,
        level=loglevel,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>"
               "{level: <8}</level> | <level>{message}</level>"
    )
    if not directory.exists():
        logger.debug(f"creating directory {directory}")
        directory.mkdir()
        logger.debug("done")
    urls = []
    threads = [
        Thread(target=fetch_url, args=(urls,))
        for _ in range(traps)
    ]
    logger.debug("fetching URLs")
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    logger.debug("done")
    logger.info("downloading traps")
    with ThreadPoolExecutor(max_workers=8) as p:
        p.map(lambda url: get(directory, url, False), urls)
    logger.info(f"downloaded {traps} traps")


if __name__ == '__main__':
    main()
