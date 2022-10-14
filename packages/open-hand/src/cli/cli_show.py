import click

from pprint import pprint

from lib.predef.config import load_config, setenv
from lib.shadowdb.shadowdb import getShadowDB
from lib.facets.authorship import displayMentionsInClusters
from lib.termio.canopies import list_canopies_counted

from .cli_base import cli


@cli.group()
def show():
    """Display canopies, cluster, configs, ..."""


@show.command()
@click.option("--env", type=click.Choice(["test", "dev", "prod"]), required=True, help="Check that config is valid")
def config(env: str):
    """Ensure config is valid"""
    print(f"Checking env {env}")
    setenv(env)
    config = load_config()
    if config is None:
        print(f"Could not find config file for env={env}")
    else:
        pprint(config)


@show.command("canopy")
@click.argument("canopy", type=str)
def canopy_show(canopy: str):
    """Show a canopy"""
    c = getShadowDB().get_canopy(canopy)
    displayMentionsInClusters(c)

@show.command("canopies")
@click.argument("index", type=int)
def canopy_list(index: int):
    """list canopies w/mention counts, starting at index"""
    list_canopies_counted(index)
