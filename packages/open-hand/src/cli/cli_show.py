import click

from pprint import pprint

from lib.predef.config import load_config, setenv
from lib.shadowdb.queries import getQueryAPI
from lib.facets.authorship import displayMentionsInClusters
from lib.termio.canopies import list_canopies_counted

from .cli_base import cli


@cli.group()
def show():
    """Display canopies, cluster, configs, ..."""


@show.command()
@click.option("--env", type=click.Choice(["test", "env", "prod"]), required=True, help="Check that config is valid")
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
    c = getQueryAPI().get_canopy(canopy)
    displayMentionsInClusters(c)


@show.command("cluster")
@click.argument("cluster_name", type=str)
def cluster_show(cluster_name: str):
    """Show the results of cluster prediction"""

    cluster = getQueryAPI().get_cluster(cluster_name)

    for item in cluster.mentions.signatures.values():
        pprint(item)

    for item in cluster.mentions.papers.values():
        pprint(item)


@show.command("canopies")
@click.argument("index", type=int)
def canopy_list(index: int):
    """list canopies w/mention counts, starting at index"""
    list_canopies_counted(index)
