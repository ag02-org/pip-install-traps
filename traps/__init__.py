import pathlib
import secrets
import urllib.parse
from multiprocessing import Pool
from threading import Thread

import click
import requests

__version__ = "1.0.0"
API_URL = "https://api.waifu.pics/nsfw/trap"


def get_traps(params):
    directory, url = params
    filename = urllib.parse.urlparse(url)
    filename = directory.joinpath(secrets.token_hex(8) + pathlib.Path(filename.path).suffix)
    with open(filename, "wb") as f:
        response = requests.get(url, stream=True)
        for block in response.iter_content(1024):
            if not block:
                break
            f.write(block)


def fetch_url(urls_list: list):
    url = requests.get(API_URL).json()["url"]
    urls_list.append(url)


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
@click.argument(
    "directory",
    default="traps",
    type=click.Path(
        dir_okay=True,
        file_okay=False,
        path_type=pathlib.Path
    )
)
def main(traps: int, directory: pathlib.Path):
    if not directory.exists():
        directory.mkdir()
    urls = []
    threads = [
        Thread(target=fetch_url, args=(urls,))
        for _ in range(traps)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    params = [
        (directory, url)
        for url in urls
    ]
    with Pool(8) as p:
        p.map(get_traps, params)


if __name__ == '__main__':
    main()
