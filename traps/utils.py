import pathlib
import urllib.parse

import loguru

logger = loguru.logger.bind(name="traps-logger")


def filename_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    filename = pathlib.Path(path).name
    return filename
