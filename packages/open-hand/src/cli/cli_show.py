import click

from pprint import pprint

from .cli_base import cli

from lib.predefs.config import load_config, setenv
from lib.db.database import get_canopy
from lib.console.display import displayMentionsInClusters
from lib.console.canopies import list_canopies_counted


@cli.group()
def show():
    """Display canopies, cluster, configs, ..."""


@show.command("cluster")
def cluster_show():
    """Show the results of cluster prediction"""
    from lib.db.database import get_cluster

    cluster = get_cluster("a mccallum_1")

    for item in cluster.mentions.signatures.values():
        pprint(item)

    for item in cluster.mentions.papers.values():
        pprint(item)


@show.command()
@click.option("--env", type=click.Choice(["testing", "production"]), required=True, help="Check that config is valid")
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
    c = get_canopy(canopy)
    displayMentionsInClusters(c)


@show.command("canopies")
@click.argument("index", type=int)
def canopy_list(index: int):
    """list canopies w/mention counts, starting at index"""
    list_canopies_counted(index)
