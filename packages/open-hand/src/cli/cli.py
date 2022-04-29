from .cli_base import cli

from . import cli_orx, cli_predict, cli_show

cli_orx  # suppress warnings
cli_predict  # suppress warnings
cli_show  # suppress warnings


def go():
    cli(obj={})


if __name__ == "__main__":
    go()
