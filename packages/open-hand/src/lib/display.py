from typing import Dict, List, Tuple
import typing as t

from pprint import pprint
from lib.db.database import add_all_referenced_signatures
from lib.predefs.typedefs import ClusterID
from itertools import groupby
import click

from lib.cli_utils import dim, yellowB


from lib.predefs.data import (
    MentionRecords,
    PaperWithSignatures,
    SignatureRec,
    get_paper_with_signatures,
    SignatureWithFocus,
    AuthorRec,
)


def format_authors(authors: List[AuthorRec], fn: t.Callable[[AuthorRec, int], str]) -> List[str]:
    return [fn(a, i) for i, a in enumerate(authors)]


def format_sig(sig: SignatureWithFocus) -> str:
    if sig.has_focus:
        return yellowB(f"{sig.signature.author_info.fullname}")
    return dim(f"{sig.signature.author_info.fullname}")


def mentions_to_displayables(
    mentions_init: MentionRecords,
) -> Tuple[MentionRecords, Dict[ClusterID, List[PaperWithSignatures]]]:
    def keyfn(s: SignatureRec):
        if s.cluster_id is None:
            return "<unclustered>"
        return s.cluster_id

    cluster_groups: Dict[str, List[SignatureRec]] = dict(
        [(k, list(grp)) for k, grp in groupby(mentions_init.signatures.values(), keyfn)]
    )

    cluster_ids = list(cluster_groups)

    mentions = add_all_referenced_signatures(mentions_init)
    cluster_tuples: List[Tuple[ClusterID, List[PaperWithSignatures]]] = []
    for id in cluster_ids:
        sig_zip_papers = [get_paper_with_signatures(mentions, sig) for sig in cluster_groups[id]]
        cluster_tuples.append((ClusterID(id), sig_zip_papers))

    cluster_dict = dict(cluster_tuples)

    return (mentions, cluster_dict)


def displayMentions(mentions: MentionRecords):
    _, cluster_dict = mentions_to_displayables(mentions)

    cluster_ids = list(cluster_dict)
    for cluster_id in cluster_ids:
        click.echo(f"Cluster is: {cluster_id}")
        cluster = cluster_dict[cluster_id]
        for pws in cluster:
            for s in pws.signatures:
                openId = s.signature.author_info.openId
                fullname = s.signature.author_info.fullname
                print(f"{fullname}  {openId}")

            paper = pws.paper
            title = click.style(paper.title, fg="blue")
            fmtsigs = [format_sig(sig) for sig in pws.signatures]
            auths = ", ".join(fmtsigs)
            click.echo(f"   {title}")
            click.echo(f"      {auths}")

        click.echo("\n")
