import click

from click.core import Context

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


@cli.command()
@click.pass_context
@click.argument("x", type=int)
@click.argument("y", type=int)
def mul(ctx: Context, x: int, y: int):
    """(mul) Testing out celery/click combo"""
    return utils.run(ctx, cs.mul, x, y)
    # return cmd.mul(x, y)


@cli.command()
@click.pass_context
def normalize(ctx: Context):
    """Normalize all un-normalized papers/signatures"""
    return utils.run(ctx, cs.normalize)


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
