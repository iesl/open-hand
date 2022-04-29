from typing import Dict, List, Tuple, Set, cast
import typing as t

from pprint import pprint

from openreview.openreview import Note
from lib.db.database import add_all_referenced_signatures
from lib.orx.open_exchange import get_notes_for_author, get_profiles
from lib.predefs.alignment import Alignment, Left, OneOrBoth, Right, Both
from lib.predefs.typedefs import ClusterID
from itertools import groupby
import click

from lib.cli_utils import dim, yellowB


from lib.predefs.data import (
    MentionRecords,
    PaperWithPrimaryAuthor,
    SignatureRec,
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
) -> Tuple[MentionRecords, Dict[ClusterID, List[PaperWithPrimaryAuthor]]]:
    def keyfn(s: SignatureRec):
        if s.cluster_id is None:
            return "<unclustered>"
        return s.cluster_id

    cluster_groups: Dict[str, List[SignatureRec]] = dict(
        [(k, list(grp)) for k, grp in groupby(mentions_init.signatures.values(), keyfn)]
    )

    cluster_ids = list(cluster_groups)

    mentions = add_all_referenced_signatures(mentions_init)
    cluster_tuples: List[Tuple[ClusterID, List[PaperWithPrimaryAuthor]]] = []

    for id in cluster_ids:
        sig_zip_papers = [PaperWithPrimaryAuthor.from_signature(mentions, sig) for sig in cluster_groups[id]]
        cluster_tuples.append((ClusterID(id), sig_zip_papers))

    cluster_dict = dict(cluster_tuples)

    return (mentions, cluster_dict)


import re

TILDE_ID_RE = re.compile("^~.+\\d$")


def is_tildeid(id: str) -> bool:
    return TILDE_ID_RE.match(id) is not None


def get_primary_tildeids(papersWithSignatures: List[PaperWithPrimaryAuthor]) -> Set[str]:
    results: List[str] = []
    for pws in papersWithSignatures:
        for s in pws.signatures:
            openId = s.signature.author_info.openId
            if s.has_focus and is_tildeid(openId):
                results.append(openId)

    uniq = set(results)
    return uniq


def get_primary_name_variants(papersWithSignatures: List[PaperWithPrimaryAuthor]) -> Set[str]:
    results: List[str] = []
    for pws in papersWithSignatures:
        for s in pws.signatures:
            fullname = s.signature.author_info.fullname
            if s.has_focus:
                results.append(fullname)

    uniq = set(results)
    return uniq


def diff_cluster_with_known_papers(cluster: List[PaperWithPrimaryAuthor]):
    tildeids = get_primary_tildeids(cluster)
    for id in tildeids:
        notes = get_notes_for_author(id)
        for note in notes:
            title = note.content.title
            noteId = note.id

def align_cluster(cluster: List[PaperWithPrimaryAuthor]) -> Dict[str, Alignment[str]]:
    tildeids = get_primary_tildeids(cluster)
    alignments: Dict[str, Alignment[str]] = dict()
    for id in tildeids:
        a = align_cluster_to_user(cluster, id)
        alignments[id] = a
    return alignments

def align_cluster_to_user(cluster: List[PaperWithPrimaryAuthor], user_id: str) -> Alignment[str]:
    author_notes = get_notes_for_author(user_id)
    aligned: List[OneOrBoth[str]] = []
    note_dict: Dict[str, Note] = dict([(cast(str, n.id), n) for n in author_notes])
    cluster_dict = dict([(c.paper.paper_id, c) for c in cluster])
    for c in cluster:
        paper_id = c.paper.paper_id
        if paper_id in note_dict:
            aligned.append(Both.of(paper_id))
        else:
            aligned.append(Left.of(paper_id))

    for n in author_notes:
        paper_id: str = n.id
        if paper_id not in cluster_dict:
            aligned.append(Right.of(paper_id))

    return Alignment(values=aligned)

def displayMentions(mentions: MentionRecords):

    _, cluster_dict = mentions_to_displayables(mentions)

    cluster_ids = list(cluster_dict)
    for cluster_id in cluster_ids:
        cluster = cluster_dict[cluster_id]

        names = get_primary_name_variants(cluster)
        tildeids = get_primary_tildeids(cluster)
        tildeidsstr = ", ".join(tildeids)
        namestr = ", ".join(names)
        click.echo(f"Cluster for {namestr}")
        click.echo(f"  Known ids: {tildeidsstr}")
        for pws in cluster:
            title = click.style(pws.paper.title, fg="blue")
            fmtsigs = [format_sig(sig) for sig in pws.signatures]
            auths = ", ".join(fmtsigs)
            click.echo(f"   {title}")
            click.echo(f"      {auths}")

        alignments = align_cluster(cluster)
        click.echo("Alignments")
        for userid, aligned in alignments.items():
            pprint(userid)
            pprint(aligned)

        click.echo("\n")
