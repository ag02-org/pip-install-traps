import pathlib
import urllib.parse


def filename_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    filename = pathlib.Path(path).name
    return filename
