import click
import sys

from click.core import Context
# import cserver as cs
# import utils
# import commands as cmd

from . import cserver as cs
from . import utils
from . import commands as cmd

app = utils.make_celery()

@click.group()
@click.option("--remote", "-x", is_flag=True, help="run command on server")
@click.pass_context
def cli(ctx: Context, remote: bool):
    ctx.ensure_object(dict)
    ctx.obj["remote"] = remote


#####
#####
#####
#####


@cli.command()
@click.argument("x", type=int)
@click.argument("y", type=int)
@click.pass_context
def add(ctx: Context, x: int, y: int):
    """(add) Testing out celery/click combo"""
    res = x + y
    print(res)
    return res


@cli.command()
@click.argument("x", type=int)
@click.argument("y", type=int)
@click.pass_context
def mul(ctx: Context, x: int, y: int):
    """(mul) Testing out celery/click combo"""
    return utils.run(ctx, cs.mul, x, y)
    # return cmd.mul(x, y)


#####
#####
#####


@cli.command()
def normalize():
    """Normalize all un-normalized papers/signatures"""
    from lib.normalizer import normalize

    normalize()


@cli.command()
@click.option("--offset", "-n", type=int, help="canopy index")
def predict(offset: int):
    """Run prediction on canopy #[offset]"""
    if offset is None:
        raise click.BadParameter("no offset provided")

    click.echo(f"offset={offset}")
    from lib.predict import run

    run(offset)


@cli.group()
def canopy():
    """Canopy related commands"""


@canopy.command("show")
@click.argument("index", type=int)
def canopyshow(index: int):
    """Show a canopy"""
    from lib.canopies import show_canopy

    show_canopy(index)


@canopy.command("list")
@click.argument("index", type=int)
def canopylist(index: int):
    """list canopies w/mention counts, starting at index"""
    from lib.canopies import list_canopies_counted

    list_canopies_counted(index)


@cli.group()
def cluster():
    """Cluster related commands"""


@cluster.command("show")
def cluster_show():
    """Show the results of cluster prediction"""

def go():
    cli(obj={})

if __name__ == "__main__":
    go()
