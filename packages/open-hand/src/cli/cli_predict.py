import click

from lib.s2andx.loaders import preload_data
from .cli_base import cli

from lib.facets.authorship import displayMentionsInClusters
from lib.s2andx.model import load_model
from lib.s2andx.predict import dopredict, predict_all


@cli.command()
@click.argument("canopy", type=str, default='')
@click.option("--profile", is_flag=True, help="profile program execution")
@click.option("--use-name-dicts", is_flag=True, help="Use (expensive to load) model data for names")
@click.option("--commit", "-c", is_flag=True, help="commit results to mongodb")
@click.option("--all", "-A", is_flag=True, help="Run prediction over all canopies")
def predict(canopy: str, commit: bool, profile: bool, use_name_dicts: bool, all: bool):
    """Run prediction on canopy"""

    if all:
        predict_all(profile=profile)
        return

    if canopy == '':
        print("Please specify a canopy or --all")
        return

    print(f"Running prediction over canopy `{canopy}`")

    pre = preload_data(use_name_counts=use_name_dicts, use_name_tuples=True)
    model = load_model()
    clusters = dopredict(canopy, commit=commit, pre=pre, profile=profile, model=model)

    for cluster in clusters:
        print(f"Mentions for cluster {cluster.cluster_id}")
        displayMentionsInClusters(cluster.mentions)
        print("")
