import click

from click.core import Context
from marshmallow.utils import pprint

from lib.predict import displayMentions
from lib.s2and_data import preload_data

# from . import cserver as cs
from . import utils

app = utils.make_celery()


@click.group()
@click.option("--remote", "-x", is_flag=True, help="run command on server")
@click.pass_context
def cli(ctx: Context, remote: bool):
    ctx.ensure_object(dict)
    ctx.obj["remote"] = remote


# @cli.command()
# @click.pass_context
# def normalize(ctx: Context):
#     """Normalize all un-normalized papers/signatures"""
#     return utils.run(ctx, cs.normalize)


@cli.command()
@click.argument("canopy", type=str)
@click.option("--commit", "-c", is_flag=True, help="commit results to mongodb")
def predict(canopy: str, commit: bool):
    """Run prediction on canopy"""

    click.echo(f"canopy={canopy}")
    from lib import predict

    pre = preload_data(use_name_counts=False, use_name_tuples=False)
    clusters = predict.dopredict(canopy, commit=commit, pre=pre)
    for cluster in clusters:
        print(f"Mentions for cluster {cluster.cluster_id}")
        displayMentions(cluster.mentions)
        print("")


@cli.command()
def predict_all():
    """Run prediction on all canopy"""
    from lib import predict

    predict.predict_all()


@cli.group()
def canopy():
    """Canopy related commands"""


@canopy.command("show")
@click.argument("canopy", type=str)
def canopy_show(canopy: str):
    """Show a canopy"""
    from lib.canopies import get_canopy

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
    from lib.database import get_cluster

    cluster = get_cluster("a mccallum_1")

    for item in cluster.mentions.signatures.values():
        pprint(item)

    for item in cluster.mentions.papers.values():
        pprint(item)


def go():
    cli(obj={})


if __name__ == "__main__":
    go()
