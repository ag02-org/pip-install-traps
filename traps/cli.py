import pathlib
import sys

import click
from loguru import logger

import traps
from traps import downloader

PATH_TYPE = click.Path(
    dir_okay=True,
    file_okay=False,
    path_type=pathlib.Path
)
CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"]
}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("-v", "--verbose", is_flag=True, help="Verbose output.")
def cli(verbose: bool):
    """How about you pip install some traps?"""
    if verbose:
        loglevel = "DEBUG"
    else:
        loglevel = "INFO"

    # Remove the default logger if it exists.
    try:
        logger.remove(0)
    except ValueError:
        pass

    logger.add(
        sys.stderr,
        level=loglevel,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>"
               "{level: <8}</level> | <level>{message}</level>",
        filter=lambda record: record["extra"].get("name") == "traps-logger"
    )


@cli.command("install")
@click.option("-n", "amount", type=int, default=10,
              show_default=True, help="Number of traps to install.")
@click.argument("directory", default="traps", type=PATH_TYPE)
def install(directory: pathlib.Path, amount: int):
    """Install (download) traps."""
    downloader.get(directory, amount)


@cli.command("version", help="Print version and exit.")
def version():
    click.echo(f"{traps.__name__} {traps.__version__}")
    sys.exit(0)


def main():
    cli.main(windows_expand_args=False)


if __name__ == "__main__":
    main()
