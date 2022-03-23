import click
import sys


@click.group()
def cli():
    pass


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
    import predict

    predict.run(offset)


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
    """Show a canopy"""
    from lib.canopies import list_canopies

    list_canopies(index)


if __name__ == "__main__":
    sys.exit(cli())
