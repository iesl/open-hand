from .cli_base import cli

# pyright: reportUnusedImport=false
# pyright: reportUnusedExpression=false

from . import cli_fetch, cli_predict, cli_show

cli_fetch  # suppress warnings
cli_predict  # suppress warnings
cli_show  # suppress warnings


def go():
    cli(obj={})


if __name__ == "__main__":
    go()
