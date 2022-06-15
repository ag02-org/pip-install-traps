import requests
import pathlib
from random import randint
import urllib.parse
from threading import Thread

api_url = "https://api.waifu.pics/nsfw/trap"


def get(directory="traps", amount=randint(5, 10)):
    path = pathlib.Path(directory)
    if not path.exists():
        path.mkdir()
    for i in range(amount):
        Thread(target=traps, args=(directory,)).start()


def traps(directory):
    req_url = requests.get(api_url)
    url = req_url.json()["url"]
    if not req_url.ok:
        print("error:", req_url)
        return
    filename = urllib.parse.urlparse(url)
    filename = pathlib.Path(directory, pathlib.Path(filename.path).name)
    with open(filename, "wb") as f:
        response = requests.get(url, stream=True)
        for block in response.iter_content(1024):
            if not block:
                break
            f.write(block)


def main():
    get()


if __name__ == '__main__':
    main()
