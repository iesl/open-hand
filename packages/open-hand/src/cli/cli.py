from dataclasses import asdict
import typing as t
import click
from click.core import Context

from lib.db.database import get_canopy
from lib.display import displayMentions
from lib.model import load_model
from lib.orx.open_exchange import get_notes_for_author
from lib.predefs.config import load_config, setenv

from lib.predefs.s2and_data import preload_data
from pprint import pprint

from . import utils

app: t.Any = utils.make_celery()

@click.group()
@click.option("--remote", "-x", is_flag=True, help="run command on server")
@click.option("--env", type=click.Choice(['testing', 'production']), default='testing', help="Check that config is valid")
@click.pass_context
def cli(ctx: Context, remote: bool, env: str):
    print(f"Env set to {env}")
    setenv(env)
    # config = load_config()
    ctx.ensure_object(dict)
    ctx.obj["remote"] = remote

@cli.command()
@click.option("--env", type=click.Choice(['testing', 'production']), required=True, help="Check that config is valid")
def check_config(env: str):
    """Ensure config is valid"""
    print(f"Checking env {env}")
    setenv(env)
    config = load_config()
    if config is None:
        print(f"Could not find config file for env={env}")
    else:
        pprint(config)

@cli.command()
@click.argument("canopy", type=str)
@click.option("--profile", is_flag=True, help="profile program execution")
@click.option("--use-name-dicts", is_flag=True, help="Use (expensive to load) model data for names")
@click.option("--commit", "-c", is_flag=True, help="commit results to mongodb")
def predict(canopy: str, commit: bool, profile: bool, use_name_dicts: bool):
    """Run prediction on canopy"""

    click.echo(f"canopy={canopy}")
    from lib import predict

    pre = preload_data(use_name_counts=use_name_dicts, use_name_tuples=True)
    model = load_model()
    clusters = predict.dopredict(canopy, commit=commit, pre=pre, profile=profile, model=model)

    for cluster in clusters:
        print(f"Mentions for cluster {cluster.cluster_id}")
        displayMentions(cluster.mentions)
        print("")


@cli.command()
@click.option("--profile", is_flag=True, help="profile program execution")
def predict_all(profile: bool):
    """Run prediction on all canopies"""
    from lib import predict

    predict.predict_all(profile=profile)


@cli.group()
def canopy():
    """Canopy related commands"""


@canopy.command("show")
@click.argument("canopy", type=str)
def canopy_show(canopy: str):
    """Show a canopy"""

    c = get_canopy(canopy)
    displayMentions(c)


@canopy.command("list")
@click.argument("index", type=int)
def canopy_list(index: int):
    """list canopies w/mention counts, starting at index"""
    from lib.canopies import list_canopies_counted

    list_canopies_counted(index)


@cli.group()
def cluster():
    """Cluster related commands"""


@cluster.command("show")
def cluster_show():
    """Show the results of cluster prediction"""
    from lib.db.database import get_cluster

    cluster = get_cluster("a mccallum_1")

    for item in cluster.mentions.signatures.values():
        pprint(item)

    for item in cluster.mentions.papers.values():
        pprint(item)


@cli.group()
def orx():
    """OpenReview exchange; fetch/update notes"""

@orx.group()
def get():
    """OpenReview exchange; fetch/update notes"""

@get.command("author")
@click.argument("authorid", type=str)
def author(authorid: str):
    notes = get_notes_for_author(authorid)
    for n in notes:
        nd = n.to_json()
        pprint(nd)

def go():
    cli(obj={})

if __name__ == "__main__":
    go()
