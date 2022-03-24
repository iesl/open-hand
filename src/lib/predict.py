from pprint import pprint
from typing import Callable, List
from lib.mongoconn import dbconn
from lib.log import logger
from lib.model import load_model, predict
from lib.canopies import CanopyMentions, get_canopy, get_canopy_strs
from s2and.data import ANDData, Author
from lib.s2and_data import preloads, setup_s2and_env

import click


def choose_canopy(n: int) -> str:
    return get_canopy_strs()[n]


def init_canopy_data(mentions: CanopyMentions):
    pre = preloads()
    anddata = ANDData(
        signatures=mentions.signatures,
        papers=mentions.papers,
        name="unnamed",
        mode="inference",  # or 'train'
        block_type="s2",  # or 'original', refers to canopy method 's2' => author_info.block is canopy
        name_tuples=pre.name_tuples,
        load_name_counts=pre.name_counts,
    )
    return anddata


def format_authors(authors: List[Author], fn: Callable[[Author, int], str]) -> List[str]:
    return [fn(a, i) for i, a in enumerate(authors)]


def dim(s: str) -> str:
    return click.style(s, dim=True)


def yellowB(s: str) -> str:
    return click.style(s, fg="yellow", bold=True)


def run(canopy_num: int):

    canopy = choose_canopy(canopy_num)
    logger.info(f"Clustering canopy '{canopy}'")
    mentions = get_canopy(canopy)
    pcount = len(mentions.papers)
    scount = len(mentions.signatures)
    logger.info(f"Mention counts papers={pcount} / signatures={scount}")
    andData = init_canopy_data(mentions)

    model = load_model()
    clusters, dist_mats = model.predict(andData.get_blocks(), andData)
    ## Show the results:
    ## TODO move this stuff elsewhere

    clustered_signatures = [[mentions.signatures[sid] for sid in cluster] for _, cluster in clusters.items()]
    clusters = [[(sig, mentions.papers[sig.paper_id]) for sig in sigcluster] for sigcluster in clustered_signatures]

    for i, cluster in enumerate(clusters):

        author_variations0 = [
            "".join(format_authors(paper.authors, lambda a, i: a.author_name if sig.author_info_position == i else ""))
            for sig, paper in cluster
        ]

        author_variations = [v for v in author_variations0 if len(v) > 0]
        names = '\n'.join([yellowB(n) for n in set(author_variations)])

        click.echo(f">> Cluster {i}")
        click.echo(f"Name Variations ")
        click.echo(names)
        for sig, paper in cluster:
            title = click.style(paper.title, fg="blue")
            authors: List[Author] = paper.authors
            position = sig.author_info_position
            authfmt = format_authors(
                authors, lambda a, i: yellowB(a.author_name) if i == position else dim(a.author_name)
            )
            auths = ", ".join(authfmt)

            click.echo(f"   {title}")
            click.echo(f"      {auths}")

        click.echo("\n")
