from typing import Callable, List, Dict, Tuple

from pprint import pprint

from lib.data import AuthorRec, ClusteringRecord, MentionRecords, PaperRec, SignatureRec
from lib.mongoconn import dbconn
from lib.log import logger
from lib.model import load_model
from lib.canopies import get_canopy, get_canopy_strs
from s2and.data import ANDData
from lib.s2and_data import preloads

import click


def choose_canopy(n: int) -> str:
    return get_canopy_strs()[n]


def init_canopy_data(mentions: MentionRecords):
    pre = preloads()
    signature_dict = mentions.signature_dict()
    paper_dict = mentions.paper_dict()
    anddata = ANDData(
        signatures=signature_dict,
        papers=paper_dict,
        name="unnamed",
        mode="inference",  # or 'train'
        block_type="s2",  # or 'original', refers to canopy method 's2' => author_info.block is canopy
        name_tuples=pre.name_tuples,
        load_name_counts=pre.name_counts,
    )
    return anddata


def format_authors(authors: List[AuthorRec], fn: Callable[[AuthorRec, int], str]) -> List[str]:
    return [fn(a, i) for i, a in enumerate(authors)]


def dim(s: str) -> str:
    return click.style(s, dim=True)


def yellowB(s: str) -> str:
    return click.style(s, fg="yellow", bold=True)


def papers2dict(ps: List[PaperRec]) -> Dict[str, PaperRec]:
    return dict([(p.paper_id, p) for p in ps])


def signatures2dict(ps: List[SignatureRec]) -> Dict[str, SignatureRec]:
    return dict([(p.signature_id, p) for p in ps])


def zip_signature_paper_pairs(mentions: MentionRecords) -> List[Tuple[SignatureRec, PaperRec]]:
    ps = mentions.papers
    return [(sig, ps[sig.paper_id]) for _, sig in mentions.signatures.items()]


def dopredict(canopy: str) -> List[ClusteringRecord]:
    # canopy = choose_canopy(canopy_num)
    logger.info(f"Clustering canopy '{canopy}'")
    mentions = get_canopy(canopy)
    pcount = len(mentions.papers)
    scount = len(mentions.signatures)
    logger.info(f"Mention counts papers={pcount} / signatures={scount}")

    andData = init_canopy_data(mentions)

    model = load_model()
    clustered_signatures, _ = model.predict(andData.get_blocks(), andData)
    cluster_records: List[ClusteringRecord] = []

    for cluster_id, sigids in clustered_signatures.items():
        sigs = [mentions.signatures[sigid] for sigid in sigids]
        papers = [mentions.papers[sig.paper_id] for sig in sigs]
        rec = ClusteringRecord(
            cluster_id=cluster_id,
            clustering_id="p.1",
            canopy=canopy,
            mentions=MentionRecords(signatures=signatures2dict(sigs), papers=papers2dict(papers)),
        )
        cluster_records.append(rec)

    return cluster_records


def dopredict00(canopy_num: int):
    canopy = choose_canopy(canopy_num)
    logger.info(f"Clustering canopy '{canopy}'")
    mentions = get_canopy(canopy)
    pcount = len(mentions.papers)
    scount = len(mentions.signatures)
    logger.info(f"Mention counts papers={pcount} / signatures={scount}")
    andData = init_canopy_data(mentions)

    model = load_model()
    clusters, _ = model.predict(andData.get_blocks(), andData)

    ## Create a new collection for clusterings
    # [{ clusteringId, clusterId, signatureId, canopyStr  }]
    # { '~', '~MSmith1;', 'sig#35', 'm smith' }
    # { 'p.1', 'm_smith_3', 'sig#35', 'm smith' }
    for clid, cluster in clusters.items():
        cluster_members = [dict(id="p.1", clid=clid, sigid=sigid, canopy=canopy) for sigid in cluster]
        dbconn.clusterings.insert_many(cluster_members)


def displayMentions(mentions: MentionRecords):
    sig_paper_pairs = zip_signature_paper_pairs(mentions)
    for sig, paper in sig_paper_pairs:
        title = click.style(paper.title, fg="blue")
        authors: List[AuthorRec] = paper.authors
        position = sig.author_info.position
        authfmt = format_authors(
            authors, lambda a, i: yellowB(a.author_name) if i == position else dim(a.author_name)
        )
        auths = ", ".join(authfmt)

        click.echo(f"   {title}")
        click.echo(f"      {auths}")

    click.echo("\n")

# def run(canopy_num: int):
#     canopy = choose_canopy(canopy_num)
#     logger.info(f"Clustering canopy '{canopy}'")
#     mentions = get_canopy(canopy)
#     pcount = len(mentions.papers)
#     scount = len(mentions.signatures)
#     logger.info(f"Mention counts papers={pcount} / signatures={scount}")
#     andData = init_canopy_data(mentions)

#     model = load_model()
#     clusters, _ = model.predict(andData.get_blocks(), andData)
#     ## Show the results:
#     ## TODO move this stuff elsewhere

#     clustered_signatures = [[mentions.signatures[sid] for sid in cluster] for _, cluster in clusters.items()]
#     clusters = [[(sig, mentions.papers[sig.paper_id]) for sig in sigcluster] for sigcluster in clustered_signatures]


#     for i, cluster in enumerate(clusters):

#         author_variations0 = [
#             "".join(format_authors(paper.authors, lambda a, i: a.author_name if sig.author_info_position == i else ""))
#             for sig, paper in cluster
#         ]

#         author_variations = [v for v in author_variations0 if len(v) > 0]
#         names = "\n".join([yellowB(n) for n in set(author_variations)])

#         click.echo(f">> Cluster {i}")
#         click.echo(f"Name Variations ")
#         click.echo(names)
#         for sig, paper in cluster:
#             title = click.style(paper.title, fg="blue")
#             authors: List[Author] = paper.authors
#             position = sig.author_info_position
#             authfmt = format_authors(
#                 authors, lambda a, i: yellowB(a.author_name) if i == position else dim(a.author_name)
#             )
#             auths = ", ".join(authfmt)

#             click.echo(f"   {title}")
#             click.echo(f"      {auths}")

#         click.echo("\n")
