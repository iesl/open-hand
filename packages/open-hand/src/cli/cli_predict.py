import click
from .cli_base import cli

from lib.console.display import displayMentionsInClusters
from lib.s2andx.model import load_model
from lib.s2andx.predict import dopredict, predict_all
from lib.predefs.s2and_data import preload_data

@cli.command()
@click.argument("canopy", type=str)
@click.option("--profile", is_flag=True, help="profile program execution")
@click.option("--use-name-dicts", is_flag=True, help="Use (expensive to load) model data for names")
@click.option("--commit", "-c", is_flag=True, help="commit results to mongodb")
def predict(canopy: str, commit: bool, profile: bool, use_name_dicts: bool):
    """Run prediction on canopy"""

    click.echo(f"canopy={canopy}")

    pre = preload_data(use_name_counts=use_name_dicts, use_name_tuples=True)
    model = load_model()
    clusters = dopredict(canopy, commit=commit, pre=pre, profile=profile, model=model)

    for cluster in clusters:
        print(f"Mentions for cluster {cluster.cluster_id}")
        displayMentionsInClusters(cluster.mentions)
        print("")


@cli.command()
@click.option("--profile", is_flag=True, help="profile program execution")
def predict_all(profile: bool):
    """Run prediction on all canopies"""

    predict_all(profile=profile)
