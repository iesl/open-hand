from typing import Dict, List, Tuple, Set, cast
import typing as t

from pprint import pprint

from openreview.openreview import Note
from lib.db.database import add_all_referenced_signatures
from lib.orx.open_exchange import get_notes_for_author
from lib.orx.profile_store import ProfileStore
from lib.orx.utils import is_tildeid
from lib.predefs.alignment import Alignment, Left, OneOrBoth, Right, Both
from lib.predefs.typedefs import ClusterID, TildeID
from itertools import groupby
import click

from lib.cli_utils import dim, yellowB


from lib.predefs.data import (
    MentionClustering,
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


def get_mention_clustering(init: MentionRecords) -> MentionClustering:
    def by_cluster(s: SignatureRec):
        return s.cluster_id if s.cluster_id is not None else "<unclustered>"

    grouped = groupby(init.signatures.values(), by_cluster)

    cluster_groups: Dict[str, List[SignatureRec]] = dict([(id, list(grp)) for id, grp in grouped])

    cluster_ids = list(cluster_groups)

    mentions = add_all_referenced_signatures(init)
    cluster_tuples: List[Tuple[ClusterID, List[PaperWithPrimaryAuthor]]] = []

    for id in cluster_ids:
        sig_zip_papers = [PaperWithPrimaryAuthor.from_signature(mentions, sig) for sig in cluster_groups[id]]
        cluster_tuples.append((ClusterID(id), sig_zip_papers))

    cluster_dict = dict(cluster_tuples)

    return MentionClustering(mentions, clustering=cluster_dict)


def get_primary_tildeids(papersWithSignatures: List[PaperWithPrimaryAuthor]) -> Set[str]:
    results: List[str] = []
    for pws in papersWithSignatures:
        for s in pws.signatures:
            openId = s.signature.author_info.openId
            if s.has_focus and is_tildeid(openId):
                results.append(openId)

    return set(results)


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


def populate_profile_store(mentions: MentionRecords) -> ProfileStore:
    ps = ProfileStore()

    for _, sig in mentions.signatures.items():
        openId = sig.author_info.openId
        if is_tildeid(openId):
            ps.add_profile(openId)

    print('Itersets')
    for s in ps.ds.itersets(with_canonical_elements=True):
        pprint(s)

    print('/Itersets')

    return ps


def displayMentionsInClusters(mentions: MentionRecords):

    clustering = get_mention_clustering(mentions)
    print("Clustering")
    # pprint(clustering)

    profile_store = populate_profile_store(clustering.mentions)

    for cluster_id in clustering.cluster_ids():
        cluster = clustering.cluster(cluster_id)
        tildeids = get_primary_tildeids(cluster)
        canonical_ids = profile_store.canonicalize_ids(list(tildeids))

        names = get_primary_name_variants(cluster)
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
