import click

from pprint import pprint
from lib.facets.authorship import createCatalogGroupForCanopy, fetch_openreview_author_catalog

from lib.predef.config import load_config, setenv
from lib.shadowdb.shadowdb import getShadowDB
from lib.termio.canopies import displayMentionsInClusters, list_canopies_counted, render_catalog_group
from lib.termio.misc_renders import render_author_catalog

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

@show.command("catalog")
@click.argument("canopy", type=str)
def show_catalog_group(canopy: str):
    """Show the authorship catalogs for given canopy"""
    canopy_diff = createCatalogGroupForCanopy(canopy)
    render_catalog_group(canopy_diff)

@show.command("canopies")
@click.argument("index", type=int)
def canopy_list(index: int):
    """list canopies w/mention counts, starting at index"""
    list_canopies_counted(index)

@show.command("author")
@click.argument("author", type=str)
def show_author(author: str):
    """Fetch and display an author profile/papers from OpenReview"""
    author_catalog = fetch_openreview_author_catalog(author)
    if author_catalog:
        render_author_catalog(author_catalog)
    else:
        print("No Profile found")
